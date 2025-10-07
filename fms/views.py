from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.views.decorators.csrf import csrf_exempt 
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Employee, Supplier, Product, Attendance
from .models import EmployeeProfile, DailyWork, Production
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import ProductionForm, BonusForm, ProductCountForm, AttendanceEditForm
from django.db.models import Sum 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from datetime import date
 
# --------------------------
# Generic CRUD helper
# --------------------------
@login_required(login_url='admin_login')
def list_items(request, model, template, context_name):
    if request.user.is_authenticated and request.user.is_staff: 
        items = model.objects.all()
    return render(request, template, {context_name: items})

@login_required(login_url='admin_login')
def add_item(request, model, fields, template, redirect_url):
    if request.user.is_authenticated and request.user.is_staff: 
        if request.method == "POST":
            data = {field: request.POST[field] for field in fields}
            model.objects.create(**data)
            return redirect('admin_redirect')  
    return render(request, template)

@login_required(login_url='admin_login')
def edit_item(request, model, sl, fields, template, redirect_url):
    if request.user.is_authenticated and request.user.is_staff: 
        item = get_object_or_404(model, sl=sl)
        if request.method == "POST":
            for field in fields:
                setattr(item, field, request.POST[field])
            item.save()
            return redirect('admin_redirect')  
    return render(request, template, {model.__name__.lower(): item})

@login_required(login_url='admin_login')
def delete_item(request, model, sl, redirect_url):
    if request.user.is_authenticated and request.user.is_staff: 
        item = get_object_or_404(model, sl=sl)
        item.delete()
    return redirect('admin_redirect')  
# --------------------------
# Employee CRUD
# --------------------------
def employee_list(request):
    return list_items(request, Employee, 'employee_list.html', 'employees')

def employee_add(request):
    return add_item(request, Employee, ['name','position','phone','email','salary'], 'employee_add.html', 'employee_list')

def employee_edit(request, sl):
    return edit_item(request, Employee, sl, ['name','position','phone','email','salary','password'], 'employee_edit.html', 'employee_list')

def employee_delete(request, sl):
    return delete_item(request, Employee, sl, 'employee_list')

# --------------------------
# Supplier CRUD
# --------------------------
def supplier_list(request):
    return list_items(request, Supplier, 'employee_list.html', 'suppliers')

def supplier_add(request):
    return add_item(request, Supplier, ['name','email','phone','Raw_Material'], 'supplier_add.html', 'supplier_list')

def supplier_edit(request, sl):
    return edit_item(request, Supplier, sl, ['name','email','phone','Raw_Material','address'], 'supplier_edit.html', 'supplier_list')

def supplier_delete(request, sl):
    return delete_item(request, Supplier, sl, 'supplier_list')

# --------------------------
# Product CRUD
# --------------------------
def product_list(request):
    return list_items(request, Product, 'product_list.html', 'products')

def product_add(request):
    return add_item(request, Product, ['name','price'], 'product_add.html', 'product_list')

def product_edit(request, sl):
    return edit_item(request, Product, sl, ['name','price'], 'product_edit.html', 'product_list')

def product_delete(request, sl):
    return delete_item(request, Product, sl, 'product_list')

# --------------------------
# Authentication & Signup
# --------------------------
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def employee_register_page(request):
    return render(request, "employee-register.html")

def supplier_register_page(request):
    return render(request, "supplier-register.html")

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            emp = Employee.objects.get(email=email, password=password)
            user, created = User.objects.get_or_create(
                username=email,
                defaults={'email': email}
            )
            auth_login(request, user)
            request.session['employee_id'] = emp.sl
            profile = get_object_or_404(EmployeeProfile, user__email=email)
            return redirect('dashboard')
        except Employee.DoesNotExist:
            pass

        supplier = Supplier.objects.filter(email=email, password=password).first()
        if supplier:
            request.session['supplier_id'] = supplier.sl
            return redirect('supplier_dashboard')

        messages.error(request, "Invalid email or password")

    return render(request, "login.html")

# --------------------------
# Supplier login page
# --------------------------
def supplier_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        supplier = Supplier.objects.filter(email=email, password=password).first()
        if supplier:
            request.session['supplier_id'] = supplier.sl
            return redirect('supplier_dashboard')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'supplier_login.html')

@csrf_exempt
def employee_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")  

        user = User.objects.create_user(username=email, email=email, password=password)
        emp= Employee.objects.create(
            name=name,
            email=email,
            password=password,
            phone=phone
        )
        EmployeeProfile.objects.create(
            user=user,
            phone=phone,
            designation="Worker",
            employee=emp   
        )
        return redirect('login_page')   
    return redirect('employee_register_page')   

@csrf_exempt
def supplier_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")   
        address = request.POST.get("address")   

        Supplier.objects.create(
            name=name,
            email=email,
            password=password,
            phone=phone,
            address=address
        )
        return redirect('login_page')  
    return redirect('supplier_register_page')  

# --------------------------
# Admin
# --------------------------
def custom_admin_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:  
                login(request, user)
                return redirect('employee_list')  
            else:
                return redirect('login') 
    else:
        form = AuthenticationForm()

    return render(request, 'admin_login.html', {'form': form})

@login_required(login_url='admin_login')
def admin_redirect(request):
    if request.user.is_authenticated and request.user.is_staff: 
        employees = Employee.objects.annotate(total_production=Sum('production__quantity'))
        return render(request, 'employee_list.html', {
            'employees': employees,
            'suppliers': Supplier.objects.all(),
            'products': Product.objects.all()
        })
    return redirect('admin_login')

def admin_logout(request):
    logout(request)  
    return redirect('admin_login')  

@login_required(login_url='admin_login')
def take_attendance(request):
    if request.user.is_authenticated and request.user.is_staff: 
        employees = EmployeeProfile.objects.all()
        if request.method == 'POST':
            today = timezone.now().date()
            for emp in employees:
                present = request.POST.get(f'attend_{emp.id}') == 'on'
                Attendance.objects.create(
                    employee=emp,
                    date=today,
                    status='IN' if present else 'OUT',
                    marked_by_admin=True
                )
            return redirect('attendance_list')
    return render(request, 'take_attendance.html', {'employees': employees})

@login_required(login_url='admin_login')
def attendance_list(request):
    if request.user.is_authenticated and request.user.is_staff: 
        attendances = Attendance.objects.select_related('employee').order_by('-timestamp')
        return render(request, 'attendance_list.html', {'attendances': attendances})

@login_required(login_url='admin_login')
def attendance_edit(request, pk):
    if request.user.is_authenticated and request.user.is_staff: 
        attendance = get_object_or_404(Attendance, pk=pk)

        if request.method == 'POST':
            form = AttendanceEditForm(request.POST, instance=attendance)
            if form.is_valid():
                form.save()
                return redirect('attendance_list')
        else:
            form = AttendanceEditForm(instance=attendance)

    return render(request, 'attendance_edit.html', {'form': form, 'attendance': attendance})

@login_required(login_url='admin_login')
def employee_bonus(request):
    if request.user.is_authenticated and request.user.is_staff: 
        employees = Employee.objects.all()
        if request.method == "POST":
            emp_id = request.POST.get("employee")
            bonus = request.POST.get("bonus")
            try:
                emp = Employee.objects.get(sl=emp_id)
                emp.salary = emp.salary + (emp.salary * int(bonus) / 100)
                emp.save()
            except Employee.DoesNotExist:
                pass
            return redirect('employee_list')  

    return render(request, 'employee_bonus.html', {"employees": employees})

# --------------------------
# Employee production
# --------------------------
def employee_dashboard(request):
    emp_id = request.session.get('employee_id')
    if not emp_id:
        return redirect('login_page')
    
    employee = Employee.objects.get(sl=emp_id)

    if request.method == 'POST':
        form = ProductionForm(request.POST)
        if form.is_valid():
            production = form.save(commit=False)
            production.employee = employee
            production.save()
            return redirect('employee_dashboard')  

    form = ProductionForm()
    productions = Production.objects.filter(employee=employee).order_by('-date')
    total_production = productions.aggregate(total=Sum('quantity'))['total'] or 0

    print(f"Productions for {employee.name}: {productions}")  

    return render(request, 'employee.html', {
        'form': form,
        'productions': productions,
        'total_production': total_production
    })

# --------------------------
# Employee dashboard
# --------------------------
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('index')

def dashboard_view(request):
        return render(request, 'dashboard.html') 

def logout_view(request):
    logout(request)   
    return redirect('login_page') 

@login_required
def dashboard(request):
    profile, _ = EmployeeProfile.objects.get_or_create(user=request.user)
    today = date.today()
    
    dailywork, _ = DailyWork.objects.get_or_create(employee=profile, date=today)

    if request.method == 'POST':
        if 'product_submit' in request.POST:
            pform = ProductCountForm(request.POST, instance=dailywork)
            if pform.is_valid():
                pform.instance.employee = profile
                pform.instance.date = today
                pform.save()

                production, created = Production.objects.get_or_create(
                    employee_profile=profile, 
                    date=today,
                    defaults={'employee': profile.employee,'quantity': dailywork.product_count}
                )
                if not created:
                    production.quantity = dailywork.product_count
                    production.save()

                messages.success(request, 'Daily product count and production history updated.')
                return redirect('dashboard')

        elif 'clock_in' in request.POST or 'clock_out' in request.POST:
            status = 'IN' if 'clock_in' in request.POST else 'OUT'
            Attendance.objects.create(employee=profile, status=status, marked_by_admin=False)
            messages.success(request, f'Attendance { "clocked in" if status=="IN" else "clocked out" }.')
            return redirect('dashboard')
    else:
        pform = ProductCountForm(instance=dailywork)

    productions = Production.objects.filter(employee_profile=profile).order_by('-date')
    total_production = productions.aggregate(total=Sum('quantity'))['total'] or 0

    last_attendances = profile.attendances.order_by('-timestamp')[:8]

    context = {
        'profile': profile,
        'pform': pform,
        'product_count': dailywork.product_count,
        'last_attendances': last_attendances,
        'today': today,
        'productions': productions,
        'total_production': total_production,
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    profile, _ = EmployeeProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

@login_required
def attendance_history(request):
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    attendances = profile.attendances.order_by('-timestamp')
    return render(request, 'attendance_history.html', {'attendances': attendances})

# --------------------------
# Supplier dashboard
# --------------------------
def supplier_dashboard(request):
    sup_id = request.session.get('supplier_id')
    if not sup_id:
        return redirect('supplier_login')

    supplier = get_object_or_404(Supplier, sl=sup_id)

    if request.method == 'POST':
        raw_material = request.POST.get('Raw_Material')
        quantity_raw = request.POST.get('Quantity')
        price_raw = request.POST.get('Price')

        # Convert to correct data types with fallback to existing values
        try:
            quantity = int(quantity_raw)
        except (ValueError, TypeError):
            quantity = supplier.Quantity

        try:
            price = int(price_raw)
        except (ValueError, TypeError):
            price = supplier.Price

        # Track if updated
        updated = False

        # Check Raw_Material update
        if raw_material and supplier.Raw_Material != raw_material:
            supplier.Raw_Material = raw_material
            updated = True

        # Check Quantity update
        if supplier.Quantity != quantity:
            supplier.Quantity = quantity
            updated = True

        # Check Price update
        if supplier.Price != price:
            supplier.Price = price
            updated = True

        if updated:
            supplier.save()
            messages.success(request, "Supplier details updated successfully.")
        else:
            messages.info(request, "No changes detected.")

    context = {
        'supplier': supplier,
    }
    return render(request, 'supplier_dashboard.html', context)



def supplier_logout(request):
    request.session.flush()
    return redirect('index')
