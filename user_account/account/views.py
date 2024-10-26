from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import Item, Contact
from .tasks import send_spam_email, send_folder_analys
from django.contrib.auth.decorators import login_required

# Create your views here.
def register(request):
    if request.method =="POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, "Account created successfully")
            return redirect("login")
    return render(request, "register.html")


def user_login(request):
    if request.method =="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentuals")
    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("login")

def home(request):
    #items = Item.objects.all() # так мы видим записи всех пользователей
    items = Item.objects.filter(created_by = request.user)
    if request.method =="POST":
        hrefname = request.POST["hrefname"]
        email = request.POST["email"]

        transobj = Contact.objects.create(hrefname=hrefname, email=email)
        transobj.save()
        send_spam_email.delay(email, hrefname)

        return redirect("finish") # видимо с методом get
    
    return render(request, "home.html", {"items": items})

def simple(request):
    items = Item.objects.filter(created_by = request.user)
    if request.method =="POST":
        hrefname = request.POST["hrefname"]
        email = request.POST["email"]

        transobj = Contact.objects.create(hrefname=hrefname, email=email)
        transobj.save()
        send_spam_email.delay(email, hrefname)
        # добавить удаление файлов и аудио через функцию

        return redirect("finish") # видимо с методом get
    
    return render(request, "simple.html", {"items": items})

def complex(request):
    items = Item.objects.filter(created_by = request.user)
    if request.method =="POST":
        hrefname = request.POST["hrefname"]
        email = request.POST["email"]

        transobj = Contact.objects.create(hrefname=hrefname, email=email)
        transobj.save()
        send_folder_analys.delay(email, hrefname)
        # добавить удаление файлов и аудио через функцию

        return redirect("finish") # видимо с методом get
    
    return render(request, "complex.html", {"items": items})


def show_finish(request):
    user = request.user.username
    return render(request, "finish.html")


def add_item(request):
    user = request.user.username
    if request.method =="POST":
        name = request.POST["name"]
        description = request.POST["description"]
        price = request.POST["price"]
        created_by = User.objects.get(username=user)

        if Item.objects.filter(name=name).exists():
            messages.error(request, "Item already exists")
        else:
            item = Item.objects.create(name=name, description=description, price=price, created_by=created_by)
            item.save()
            
            return redirect("home")
    return render(request, "add.html")

def edit_item(request):
    items = Item.objects.filter(created_by = request.user)
    return render(request, "edit.html", {"items": items})

@login_required
def update_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, created_by=request.user)
    if request.method == "POST":
        item.name = request.POST.get("name")
        item.description = request.POST.get("description")
        item.price = request.POST.get("price")
        item.save()
        return redirect("home")
    return render(request, "update.html", {"item": item})

@login_required
def delete_item(request, id):
    item = Item.objects.get(id=id)
    item.delete()
    return redirect("edit")