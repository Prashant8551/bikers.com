from django.shortcuts import render,HttpResponse,redirect
from bikeapp import urls
from bikeapp.models import Product, Cart, Order,MyOrder
from django.contrib.auth.models import User 
from django.contrib.auth import login , logout, authenticate
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail


# Create your views here.
def register(request):
    if request.method =='GET':
        return render(request , "register.html")
    else:
        nm = request.POST['uname']
        p = request.POST['upass']
        cp = request.POST['ucpass']
        # print(nm)
        # print(p)
        # print(cp)
        context ={}
        if p != cp :
            context['error'] = "password do not Match"
            return render(request, "register.html", context)
        elif len(p) > 5:
            context['error'] = "password should be less than 6"
            return render(request, "register.html", context)
        else:
            try:
                u =User.objects.create(username = nm)
                u.set_password(p)
                u.save()
                context['success'] = "successfully registered"
                return render(request, "register.html", context)
            except:
                context['error'] = "user alredy exist"
                return render(request, "register.html", context)

def user_login(request):
    if request.method =='GET':
        return render(request ,"login.html")
    else:
        nm = request.POST['uname']
        p = request.POST['upass']
        u = authenticate(username = nm, password =p)
        if u is not None:
            login(request, u)
            return redirect("/home")
        else:
            context ={}
            context['error'] = 'user or password is incorrect ..'
            return render(request, "login.html" ,context)


def home(request):
    m =Product.objects.filter(is_active = True)
    print(m)
    context={}
    context['data'] = m
    return render(request ,"index.html",context)


def product_details(request,prod_id):
    p =Product.objects.filter(id = prod_id)
    context= {}
    context ['data'] = p
    return render(request, 'product details.html',context)
    

def cart(request,prod_id):
    if request.user.is_authenticated:
        u=User.objects.filter(id=request.user.id)
        # print(u[0])
        p =Product.objects.filter(id=prod_id)

        q1=Q(user_id = u[0])
        q2=Q(pid_id = p[0])
        c=Cart.objects.filter(q1 & q2)
        n =len(c)
        context={}
        context['data']=p
        if n==1:
            context['msg'] = "product alredy exicts in cart"
            return render(request,"product details.html",context)
        else:
            c = Cart.objects.create(user_id =u[0],pid = p[0])
            c.save()
            context['msg1'] ="product succesfully added to cart !!"
            return render(request,"product details.html",context)
    else:# if not authenticate
        return redirect("/login")
    
def user_logout(request):
    logout(request)
    return render(request,"login.html")

def search(request):
    context = {}
    query = request.POST['query']   # bracket madhla query he html page madhe form tag madhe name aahe te dila
    print(query)
    pname = Product.objects.filter(name__icontains = query) # sql chya like operator type aahe hi query
    pdetails = Product.objects.filter(pdetails__icontains = query)  # icontains like operator sarkh use hot aahe
    pcat = Product.objects.filter(cat__icontains = query)  # je bracket madhe name aahe te table name ani te kontya varible madhe store
    allproducts = pname.union(pdetails, pcat)
    if len(allproducts) == 0:
        context['errmsg'] = "Products Not Found"
    context['data'] = allproducts
    return render(request, "index.html", context)
    return HttpResponse("query fetched!!")
        
    
def updateqty(request , x,cid):
    c = Cart.objects.filter(id =cid)
    q =c[0].qty
    if x == '1' :
        q=q+1
    elif q>1:
        q =q-1
    c.update(qty = q)
    return redirect("/viewcart")

def viewcart(request):
    c = Cart.objects.filter(user_id = request.user.id)
    
    tot =0
    for x in c:
        tot = tot + x.pid.price * x.qty
    context={}
    context['data'] =c
    context['totamt'] =tot
    context['n'] =len(c)
    return render(request,"cart.html",context)

def remove(request, cid):
    c = Cart.objects.filter(id =cid)
    c.delete()
    context={}
    context['data'] =c
    return redirect("/viewcart") 

def remove_order(request, oid):
    o = Cart.objects.filter(id =oid)
    o.delete()
    context={}
    context['data'] =o
    return redirect("/fetchorder") 

def placeorder(request):
    c = Cart.objects.filter(user_id = request.user.id)
    o_id = random.randrange(1000,9999)   
    for x in c:
        amount =x.pid.price * x.qty
        o = Order.objects.create(order_id = o_id ,user_id= x.user_id,
                                 amt=amount, qty = x.qty, pid =x.pid)
        o.save()
        x.delete()
    return redirect("/fetchorder")

def fetchorder(request):
    orders =Order.objects.filter(user_id = request.user.id)
    tot =0
    for x in orders:
        tot = tot + x.amt

    context= {}
    context['orders']= orders
    context['tamt']= tot
    context['n']= len(orders)
    return render(request,"placeorder.html",context)

def makepayment(request):
    client = razorpay.Client(auth=("rzp_test_R7kWkFU6ZllnWF", "W0gE85soRmV6WanAQr1nW69n"))
    Ord= Order.objects.filter(user_id= request.user.id)
    tot=0
    for x in Ord:
        tot= tot+x.amt
        oid=x.order_id

    data = {"amount":tot*100,"currency": "INR", "receipt": oid}
    payment =client.order.create(data = data)
    print(payment)
    context ={}
    context['payment']=payment
    return render(request,"pay.html",context)

def paymentsuccess(request):
    sub ="Ekart-Order status"
    msg = "your order successfully palaced..."
    frm = "suryawanshiprashant143@gmail.com"
    u = User.objects.filter(id = request.user.id)
    to =u[0]
    print(to)
    send_mail(
        sub,
        msg,
        frm,
        [to], 
        fail_silently=False
        )
    ord = Order.objects.filter(id = request.user.id)
    for x in ord:
        mo = MyOrder.objects.create(order_id = x.order_id,
                                    user_id= x.user_id,
                                    pid= x.pid,
                                    qty =x.qty,
                                    amt= x.amt)
        mo.save()
        x.delete()
        
    return render(request,"sucess.html")
    
def catfilter(request, cv):
    print(cv)
    if cv == '1':
        q1 = Q(cat = 'normal bikes')
    elif cv == '2':
        q1 = Q(cat = 'sports')
    else:
        q1 = Q(cat = 'parts')

    q2 = Q(is_active = True)

    p = Product.objects.filter(q1 & q2)
    print(p)
    context = {}
    context['data'] = p
    return render(request, "index.html", context)


def sort(request, sv):
    if sv == '1':
        p = Product.objects.order_by('-price').filter(is_active = True)
    else:
        p = Product.objects.order_by('price').filter(is_active = True)
    context = {}
    context['data'] = p   
    return render(request, "index.html", context)

def filterbyprice(request):
    min = request.POST['min']
    max = request.POST['max']

    q1 = Q(price__gte = min)
    q2 = Q(price__lte = max)

    p = Product.objects.filter(q1 & q2)
    context = {}
    context['data'] = p
    return render(request, "index.html", context)

def about(request):
    return render(request, "About us.html")

def contact(request):
    return render(request,"Contact us.html")