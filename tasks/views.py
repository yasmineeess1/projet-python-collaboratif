
from django.shortcuts import render, redirect
from .models import Task, TaskHistory
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

@login_required
def list_tasks(request):
    query = request.GET.get('q')

    if query:
        tasks = Task.objects.filter(user=request.user, title__icontains=query)
    else:
        tasks = Task.objects.filter(user=request.user)

    if request.method == 'POST':
        title = request.POST['title']
        priority = request.POST.get('priority', 'medium')
        task = Task.objects.create(title=title, priority=priority, user=request.user)
        TaskHistory.objects.create(task=task, user=request.user, action="création")

        return redirect('/')

    context = {'tasks': tasks}
    return render(request, 'tasks/list.html', context)



def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    TaskHistory.objects.create(task=task, user=request.user, action="suppression")
    task.delete()
    return redirect('/')

    
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            TaskHistory.objects.create(task=task, user=request.user, action="modification")
            return redirect('/')
    else:
        form = TaskForm(instance=task)

    context = {'form': form, 'edit': True, 'task': task}
    return render(request, 'tasks/edit.html', context)

def toggle_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.completed = not task.completed
    task.save()
    action = "complétée" if task.completed else "reouverte"
    TaskHistory.objects.create(task=task, user=request.user, action=action)
    return redirect('/')


def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()

    if total_tasks > 0:
        completion_percentage = round((completed_tasks / total_tasks) * 100, 2)
    else:
        completion_percentage = 0

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_percentage': completion_percentage,
    }

    return render(request, 'tasks/dashboard.html', context)

@login_required
def task_history(request):  # ✅ Bien indenté
    history = TaskHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'tasks/history.html', {'history': history})


def export_pdf(request):
    tasks = Task.objects.all().order_by('-created')
    template_path = 'tasks/export_pdf.html'
    context = {'tasks': tasks}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="todolist.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    return response