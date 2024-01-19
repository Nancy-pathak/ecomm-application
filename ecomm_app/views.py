from django.shortcuts import render,HttpResponse,redirect
from django.views import View #to import class
from django.contrib.auth import authenticate,login,logout
from .models import product,cart, order
import random
import razorpay
#---------------------------------------------------------------------
def home(request):
    #to display all admin panel data in home page
    context={} # to display any data on make we need to make dictionary 
    p=product.objects.filter(is_active=True)
    context['products']=p # products(name) will be anything 
    #print(p) display data in terminal
    return render(request, 'index.html',context)

# to acces id to see datils
def pdetails(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def viewcart(request):
    return render(request,'cart.html')

#for login page
def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        if uname=="" or upass=="":
            # for access html file or print on chrome for showing alert   
            context={}
            context['errormsg']="Field can't be empty- plz check it out !"
            return render(request,'login.html',context)
        else:
            # for authentication that user login successfully
            u=authenticate(username=uname,password=upass)
            if u is not None: ##username and password are not blank means it does not contain null value then login and redirect to home page
                login(request,u)
                return redirect('/home')
            else:
                #it check register user is login or not it shows eroor
                context={}
                context['errormsg']="Invalid username and password "
                return render(request,'login.html',context)  
    else:
        return render(request,'login.html')

# for register page 
from django.contrib.auth.models import User
def register(request):
    if request.method=='POST':
        #here uname,upass are the name feild in our input form 
        # we access input feild in html using name feild
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        #when we click register it access empty so we dont to access empty field so that we write:
        if uname=="" or upass==""  or ucpass=="":
        # for access html file or print on chrome for showing alert   
            context={}
            context['errormsg']="Field can't be empty- plz check it out !"
            return render(request,'register.html',context)
        
        # for confirmation of password password should be same as confirm password
        elif upass!=ucpass:
            context={}
            context['errormsg']="Password didn't match- plz check it out !"
            return render(request,'register.html',context)
        else:
            #exception handling for when we enter duplicate data we need to know that username alredy exist so that we are going to write in try and except block 
            try:
                u=User.objects.create(username=uname,password=upass,email=uname) #we write username in email #orm query
                u.set_password(upass) #for hiding password show encypted password
                u.save()
                #for sucess message we write code in html file
                context={}
                context['success']="User created successfully"
                return render(request,'register.html',context)
        
            except Exception:
                context={}
                context['errormsg']="Username already exist"
                return render(request,'register.html',context)          
    else:
        return render(request,'register.html')
    
#logout function
def user_logout(request):
    logout(request)
    return redirect('/home')

# for filter value
from django.db.models import Q

def catfilter(request,cv): #cv will be anything when we want to pass number we need variable here we use cv
    q1=Q(is_active=True) #q1(variable name) is base class here it will be anything 
    q2=Q(cat=cv) #import  q
    p=product.objects.filter(q1&q2) # to check both condition
    # to pass take dict
    context={}
    context['products']=p
    return render(request,'index.html',context)

# sort by price
def sort(request,sv):
    if sv == '0':
        col='price' #print in asending order
    else:
        col='-price' #print in decending order
    # pass in orm query
    p=product.objects.order_by(col)
    context={}
    context['products']=p
    return render(request, 'index.html' ,context)

# to pass range filter by price
def range(request):
    min=request.GET['min'] #index.html name="min"
    max=request.GET['max']
    q1=Q(price__gte=min) #greater than equal to
    q2=Q(price__lte=max) # price column name
    q3=Q(is_active=True) #column name
    p=product.objects.filter(q1&q2&q3)
    context={}
    context['products']=p
    return render(request, 'index.html' ,context)

#for cart msg
def addtocart(request,pid):
    userid=request.user.id #to check which user is login or which user added product in cart
    u=User.objects.filter(id=userid) 
    print(u[0]) 
    #how to insert data
    p=product.objects.filter(id=pid) 
    print(p[0])
    #-----to check how many product added in the cart
    q1=Q(uid=u[0]) 
    q2=Q(pid=p[0])
    c=cart.objects.filter(q1 and q2)
    n=len(c) 
    context={}
    context['products']=p
    if n==1:
        context['msg']='product already exist in the cart'
    
    else:
        c=cart.objects.create(uid=u[0],pid=p[0])
        c.save()
        # for sucess msg
        # context={}
        # context['products']=p
        context['success']="product added succesfully in the card" #for success msg
    return render(request,'product_details.html',context)

def viewcart(request):
    if request.user.is_authenticated: #view cart login check
       c=cart.objects.filter(uid=request.user.id)
       np=len(c)         #to calculate the en of product
       s=0
       for x in c:
          s=s+x.pid.price*x.qty

       print(s)
        # print(x.pid.price)
    # print(c[0])
    # print(c[0].pid)
    # print(c[0].uid)
    # print(c[0].pid.name)
    # print(c[0].uid.is_superuser)
       context={}
       context['products']=c
       context['total']=s
       context['n']=np
    
       return render(request, 'cart.html',context)
    else:  #if not than go to login page
        return redirect('/login')


def remove(request,cid):
    c=cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=cart.objects.filter(id=cid)
    # print(c)
    # print(c[0])
    # print(c[0].qty)
    if qv == '1':
        t=c[0].qty+1
        c.update(qty=t)
    
    else:
        if c[0].qty > 1:
            t=c[0].qty-1
            c.update(qty=t)

    return redirect("/viewcart")

def placeorder(request):
    userid=request.user.id 
    # print(userid)
    c=cart.objects.filter(uid=userid)
    # print(c)
    oid=random.randrange(1000,9999)
    # print(oid)
    for x in c:
        # print(x)
        # print(x.pid)
        # print(x.qty)
        o=order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty) #it is taken from models
        o.save() #shift data into order table
        x.delete() #delete records from cart table
    # return HttpResponse("Place order successfully!!!")
        
    orders=order.objects.filter(uid=userid)
    np=len(orders)         #to calculate the en of product
    s=0
    for x in orders:
        s=s+x.pid.price*x.qty

    print(s)
        
    context={}
    context['products']=orders
    context['total']=s
    context['n']=np
    

    return render(request,'placeorder.html',context)

def makepayment(request):
   orders=order.objects.filter(uid=request.user.id)
   s=0
   for x in orders:
        s=s+x.pid.price*x.qty
        oid=x.order_id
    
   client = razorpay.Client(auth=("rzp_test_R11BzRqhp5wLzD", "8kl9NetiVMzD0iW6zy6zZITN"))

   DATA = {
    "amount": s*100, # OR s*10 if it will give error
    "currency": "INR",
    "receipt": oid,
    "notes": {
        "key1": "value3",
        "key2": "value2"
        }
   }
   payment=client.order.create(data = DATA)
   print(payment)
   uname=request.user.username
   print(uname)
   context={}
   context['data']=payment

   client.order.create(data = DATA)
#    return HttpResponse("In Payment Section")
   return render(request,'pay.html',context)