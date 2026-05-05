from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Enrollment, LessonProgress
from .forms import TeacherCourseForm


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, 'courses/course_list.html', {
        'courses': courses
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)

    is_enrolled = False
    progress_percent = 0

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).first()

        if enrollment:
            is_enrolled = True
            progress_percent = enrollment.progress

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'progress_percent': progress_percent,
    })


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    return redirect('course_detail', slug=course.slug)


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.course

    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).first()

    if not enrollment:
        return redirect('course_detail', slug=course.slug)

    lessons = list(course.lessons.all().order_by('order', 'id'))
    current_index = lessons.index(lesson)

    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None

    is_completed = LessonProgress.objects.filter(
        student=request.user,
        lesson=lesson,
        completed=True
    ).exists()

    context = {
        'lesson': lesson,
        'course': course,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'lessons': lessons,
        'is_completed': is_completed,
    }

    return render(request, 'courses/lesson_detail.html', context)


@login_required
def complete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.course

    LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'completed': True}
    )

    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).first()

    if enrollment:
        total_lessons = course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course,
            completed=True
        ).count()

        if total_lessons > 0:
            progress = int((completed_lessons / total_lessons) * 100)
        else:
            progress = 0

        enrollment.progress = progress
        enrollment.completed = progress == 100
        enrollment.save()

    return redirect('lesson_detail', pk=lesson.pk)


@login_required
def teacher_course_create(request):
    if request.user.profile.role != 'teacher':
        return redirect('dashboard')

    if request.method == 'POST':
        form = TeacherCourseForm(request.POST, request.FILES)

        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()

            return redirect('dashboard')

    else:
        form = TeacherCourseForm()

    context = {
        'form': form
    }

    return render(request, 'courses/teacher_course_create.html', context)