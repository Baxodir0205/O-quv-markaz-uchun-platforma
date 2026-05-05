from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from education.models import Group
from accounts.models import Profile
from cases.models import CaseStudy, CaseSubmission

from .models import (
    Lesson,
    Assignment,
    Submission,
    Test,
    TestQuestion,
    TestResult,
    TestAnswer,
)


def model_has_field(model, field_name):
    return any(field.name == field_name for field in model._meta.fields)


def teacher_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')

        if not hasattr(request.user, 'profile'):
            return redirect('/login/')

        if request.user.profile.role != 'teacher':
            return redirect('/student/')

        return view_func(request, *args, **kwargs)

    return wrapper


def student_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')

        if not hasattr(request.user, 'profile'):
            return redirect('/login/')

        if request.user.profile.role != 'student':
            return redirect('/teacher/')

        return view_func(request, *args, **kwargs)

    return wrapper


def teacher_groups_qs(user):
    return Group.objects.filter(
        teacher_groups__teacher=user
    ).distinct()


@login_required
@teacher_only
def teacher_dashboard(request):
    groups = teacher_groups_qs(request.user)

    students_count = Profile.objects.filter(
        role='student',
        group__in=groups
    ).count()

    latest_submissions = Submission.objects.filter(
        assignment__teacher=request.user
    ).select_related('student', 'assignment').order_by('-created_at')[:5]

    unchecked_assignments = Submission.objects.filter(
        assignment__teacher=request.user,
        checked=False
    ).count()

    if model_has_field(CaseSubmission, 'status'):
        unchecked_cases = CaseSubmission.objects.filter(
            case__teacher=request.user,
            status='submitted'
        ).count()
    else:
        unchecked_cases = 0

    return render(request, 'dashboard/teacher_dashboard.html', {
        'groups_count': groups.count(),
        'students_count': students_count,
        'lessons_count': Lesson.objects.filter(teacher=request.user).count(),
        'assignments_count': Assignment.objects.filter(teacher=request.user).count(),
        'tests_count': Test.objects.filter(teacher=request.user).count(),
        'cases_count': CaseStudy.objects.filter(teacher=request.user).count(),
        'unchecked_submissions': unchecked_assignments + unchecked_cases,
        'latest_submissions': latest_submissions,
    })


@login_required
@teacher_only
def teacher_groups(request):
    groups = teacher_groups_qs(request.user)

    return render(request, 'dashboard/teacher_groups.html', {
        'groups': groups
    })


@login_required
@teacher_only
def teacher_group_detail(request, group_id):
    group = get_object_or_404(teacher_groups_qs(request.user), id=group_id)

    students = Profile.objects.filter(
        role='student',
        group=group
    ).select_related('user')

    return render(request, 'dashboard/teacher_group_detail.html', {
        'group': group,
        'students': students
    })


@login_required
@teacher_only
def teacher_students(request):
    groups = teacher_groups_qs(request.user)
    search = request.GET.get('q', '').strip()

    students = Profile.objects.filter(
        role='student',
        group__in=groups
    ).select_related('user', 'group').order_by('full_name')

    if search:
        students = students.filter(
            Q(full_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(group__name__icontains=search)
        )

    return render(request, 'dashboard/teacher_students.html', {
        'students': students,
        'search': search,
    })


@login_required
@teacher_only
def teacher_lessons(request):
    groups = list(teacher_groups_qs(request.user))

    for group in groups:
        group.lessons_count = Lesson.objects.filter(
            teacher=request.user,
            group=group
        ).count()

    return render(request, 'dashboard/teacher_lessons.html', {
        'groups': groups
    })


@login_required
@teacher_only
def teacher_group_lessons(request, group_id):
    group = get_object_or_404(teacher_groups_qs(request.user), id=group_id)

    lessons = Lesson.objects.filter(
        teacher=request.user,
        group=group
    ).order_by('-created_at')

    return render(request, 'dashboard/teacher_group_lessons.html', {
        'group': group,
        'lessons': lessons
    })


@login_required
@teacher_only
def create_lesson(request):
    groups = teacher_groups_qs(request.user)
    selected_group_id = request.GET.get('group')

    if request.method == 'POST':
        group_id = request.POST.get('group')

        if not group_id:
            messages.error(request, "Guruh tanlang!")
            return redirect('dashboard:create_lesson')

        Lesson.objects.create(
            teacher=request.user,
            group_id=group_id,
            title=request.POST.get('title') or 'Nomsiz dars',
            description=request.POST.get('description') or '',
            content=request.POST.get('content') or '',
            file=request.FILES.get('file'),
            video_link=request.POST.get('video_link') or None,
        )

        messages.success(request, "Dars qo‘shildi!")
        return redirect('dashboard:teacher_group_lessons', group_id=group_id)

    return render(request, 'dashboard/create_lesson.html', {
        'groups': groups,
        'selected_group_id': selected_group_id,
    })


@login_required
@teacher_only
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, teacher=request.user)
    group_id = lesson.group.id
    lesson.delete()

    messages.success(request, "Dars o‘chirildi!")
    return redirect('dashboard:teacher_group_lessons', group_id=group_id)


@login_required
@teacher_only
def teacher_assignments(request):
    assignments = list(
        Assignment.objects.filter(
            teacher=request.user
        ).select_related('group').order_by('-created_at')
    )

    for assignment in assignments:
        submissions = assignment.submissions.all()
        assignment.total_submissions = submissions.count()
        assignment.checked_submissions = submissions.filter(checked=True).count()
        assignment.unchecked_submissions = submissions.filter(checked=False).count()

    return render(request, 'dashboard/teacher_assignments.html', {
        'assignments': assignments
    })


@login_required
@teacher_only
def create_assignment(request):
    groups = teacher_groups_qs(request.user)

    if request.method == 'POST':
        group_id = request.POST.get('group')

        if not group_id:
            messages.error(request, "Guruh tanlang!")
            return redirect('dashboard:create_assignment')

        assignment = Assignment(
            teacher=request.user,
            group_id=group_id,
            title=request.POST.get('title') or 'Nomsiz vazifa',
            description=request.POST.get('description') or '',
            deadline=request.POST.get('deadline') or None,
            file=request.FILES.get('file'),
        )

        if hasattr(assignment, 'max_score'):
            assignment.max_score = request.POST.get('max_score') or 100

        assignment.save()

        messages.success(request, "Vazifa yaratildi!")
        return redirect('dashboard:teacher_assignments')

    return render(request, 'dashboard/create_assignment.html', {
        'groups': groups
    })


@login_required
@teacher_only
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        teacher=request.user
    )

    submissions = Submission.objects.filter(
        assignment=assignment
    ).select_related('student').order_by('-created_at')

    return render(request, 'dashboard/assignment_submissions.html', {
        'assignment': assignment,
        'submissions': submissions
    })


@login_required
@teacher_only
def grade_submission(request, submission_id):
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        assignment__teacher=request.user
    )

    if request.method == 'POST':
        submission.score = request.POST.get('score') or 0
        submission.feedback = request.POST.get('feedback') or ''
        submission.checked = True

        if hasattr(submission, 'checked_at'):
            submission.checked_at = timezone.now()

        submission.save()
        messages.success(request, "Vazifa baholandi!")

    return redirect(
        'dashboard:assignment_submissions',
        assignment_id=submission.assignment.id
    )


@login_required
@teacher_only
def teacher_tests(request):
    tests = list(
        Test.objects.filter(
            teacher=request.user
        ).select_related('group').prefetch_related('questions').order_by('-created_at')
    )

    for test in tests:
        test.total_questions = test.questions.count()

        students = Profile.objects.filter(
            role='student',
            group=test.group
        )

        test.students_count = students.count()

        test.solved_count = TestResult.objects.filter(
            test=test
        ).values('student').distinct().count()

    return render(request, 'dashboard/teacher_tests.html', {
        'tests': tests
    })


@login_required
@teacher_only
def create_test(request):
    groups = teacher_groups_qs(request.user)

    if request.method == 'POST':
        group_id = request.POST.get('group')
        title = request.POST.get('title') or 'Nomsiz test'
        description = request.POST.get('description') or ''

        questions = request.POST.getlist('question[]')
        option_as = request.POST.getlist('option_a[]')
        option_bs = request.POST.getlist('option_b[]')
        option_cs = request.POST.getlist('option_c[]')
        option_ds = request.POST.getlist('option_d[]')
        correct_answers = request.POST.getlist('correct_answer[]')

        if not group_id:
            messages.error(request, "Guruh tanlang!")
            return redirect('dashboard:create_test')

        test = Test.objects.create(
            teacher=request.user,
            group_id=group_id,
            title=title,
            description=description,
        )

        added_count = 0

        for i in range(len(questions)):
            question_text = questions[i].strip() if i < len(questions) else ''

            if question_text:
                TestQuestion.objects.create(
                    test=test,
                    question=question_text,
                    option_a=option_as[i] if i < len(option_as) else '',
                    option_b=option_bs[i] if i < len(option_bs) else '',
                    option_c=option_cs[i] if i < len(option_cs) else '',
                    option_d=option_ds[i] if i < len(option_ds) else '',
                    correct_answer=correct_answers[i] if i < len(correct_answers) else 'A',
                )
                added_count += 1

        if added_count == 0:
            test.delete()
            messages.error(request, "Kamida 1 ta savol kiriting!")
            return redirect('dashboard:create_test')

        messages.success(request, f"Test yaratildi! Savollar soni: {added_count}")
        return redirect('dashboard:teacher_tests')

    return render(request, 'dashboard/create_test.html', {
        'groups': groups
    })


@login_required
@teacher_only
def test_results(request, test_id):
    test = get_object_or_404(
        Test,
        id=test_id,
        teacher=request.user
    )

    group = test.group
    total_questions = test.questions.count()

    students = list(
        Profile.objects.filter(
            role='student',
            group=group
        ).select_related('user').order_by('full_name')
    )

    for profile in students:
        result = TestResult.objects.filter(
            student=profile.user,
            test=test
        ).first()

        if result:
            profile.total_questions = result.total_questions
            profile.solved_count = result.total_questions
            profile.correct_count = result.correct_count
            profile.result = result
        else:
            profile.total_questions = total_questions
            profile.solved_count = 0
            profile.correct_count = 0
            profile.result = None

    return render(request, 'dashboard/test_results.html', {
        'test': test,
        'group': group,
        'students': students,
        'total_questions': total_questions,
    })
@login_required
@teacher_only
def delete_test(request, test_id):
    test = get_object_or_404(
        Test,
        id=test_id,
        teacher=request.user
    )

    if request.method == 'POST':
        test.delete()
        messages.success(request, "Test o‘chirildi!")
        return redirect('dashboard:teacher_tests')

    return redirect('dashboard:teacher_tests')

@login_required
@teacher_only
def teacher_cases(request):
    cases = CaseStudy.objects.filter(
        teacher=request.user
    ).select_related('group').order_by('-created_at')

    return render(request, 'dashboard/teacher_cases.html', {
        'cases': cases
    })


@login_required
@teacher_only
def create_case(request):
    groups = teacher_groups_qs(request.user)

    if request.method == 'POST':
        group_id = request.POST.get('group')
        level = request.POST.get('level') or 'easy'

        if not group_id:
            messages.error(request, "Guruh tanlanmagan!")
            return redirect('dashboard:create_case')

        if level == 'easy':
            xp_reward = 20
            coin_reward = 10
        elif level == 'medium':
            xp_reward = 40
            coin_reward = 20
        else:
            xp_reward = 70
            coin_reward = 35

        case = CaseStudy(
            teacher=request.user,
            group_id=group_id,
            title=request.POST.get('title') or 'Nomsiz case',
            short_description=request.POST.get('short_description') or '',
            situation=request.POST.get('situation') or '',
            task=request.POST.get('task') or '',
            expected_result=request.POST.get('expected_result') or '',
            thumbnail=request.FILES.get('thumbnail'),
            level=level,
            xp_reward=xp_reward,
            coin_reward=coin_reward,
            is_published=True
        )

        case.save()

        messages.success(request, "Case Study yaratildi!")
        return redirect('dashboard:teacher_cases')

    return render(request, 'dashboard/create_case.html', {
        'groups': groups
    })


@login_required
@teacher_only
def case_submissions(request, case_id):
    case = get_object_or_404(
        CaseStudy,
        id=case_id,
        teacher=request.user
    )

    submissions = CaseSubmission.objects.filter(
        case=case
    ).select_related('student').order_by('-submitted_at')

    return render(request, 'dashboard/case_submissions.html', {
        'case': case,
        'submissions': submissions
    })


@login_required
@teacher_only
def grade_case_submission(request, submission_id):
    submission = get_object_or_404(
        CaseSubmission,
        id=submission_id,
        case__teacher=request.user
    )

    if request.method == 'POST':
        submission.score = request.POST.get('score') or 0
        submission.feedback = request.POST.get('feedback') or ''

        if hasattr(submission, 'status'):
            submission.status = 'checked'

        if hasattr(submission, 'checked_at'):
            submission.checked_at = timezone.now()

        submission.save()
        messages.success(request, "Case Study baholandi!")

    return redirect(
        'dashboard:case_submissions',
        case_id=submission.case.id
    )


@login_required
@student_only
@login_required
@student_only
def student_dashboard(request):
    profile = request.user.profile
    group = profile.group

    if not group:
        return render(request, 'dashboard/student_dashboard.html', {
            'group': None,
            'profile': profile,
            'lessons_count': 0,
            'assignments_count': 0,
            'tests_count': 0,
            'cases_count': 0,
        })

    lessons = Lesson.objects.filter(group=group)
    assignments = Assignment.objects.filter(group=group)
    tests = Test.objects.filter(group=group)
    cases = CaseStudy.objects.filter(group=group, is_published=True)

    return render(request, 'dashboard/student_dashboard.html', {
        'group': group,
        'profile': profile,
        'lessons_count': lessons.count(),
        'assignments_count': assignments.count(),
        'tests_count': tests.count(),
        'cases_count': cases.count(),
    })

@login_required
@student_only
def student_lessons(request):
    group = request.user.profile.group

    lessons = Lesson.objects.filter(
        group=group
    ).select_related('group').order_by('-created_at')

    return render(request, 'dashboard/student_lessons.html', {
        'group': group,
        'lessons': lessons,
    })
@login_required
@student_only
def student_assignments(request):
    profile = request.user.profile
    group = profile.group

    assignments = Assignment.objects.filter(
        group=group
    ).select_related('group').order_by('-created_at')

    submissions = Submission.objects.filter(
        student=request.user,
        assignment__in=assignments
    ).select_related('assignment')

    submitted_assignments = submissions.values_list(
        'assignment_id', flat=True
    )

    return render(request, 'dashboard/student_assignments.html', {
        'group': group,
        'assignments': assignments,
        'submissions': submissions,
        'submitted_assignments': list(submitted_assignments),
    })
@login_required
@student_only
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        group=request.user.profile.group
    )

    submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()

    if request.method == 'POST':
        if submission:
            submission.answer_text = request.POST.get('answer_text') or ''
            new_file = request.FILES.get('file')

            if new_file:
                submission.file = new_file

            submission.checked = False
            submission.score = 0

            if hasattr(submission, 'feedback'):
                submission.feedback = ''

            submission.save()
            messages.success(request, "Javob yangilandi!")
        else:
            Submission.objects.create(
                assignment=assignment,
                student=request.user,
                answer_text=request.POST.get('answer_text') or '',
                file=request.FILES.get('file')
            )

            messages.success(request, "Vazifa topshirildi!")

        return redirect('dashboard:student_assignments')

    return render(request, 'dashboard/submit_assignment.html', {
        'assignment': assignment,
        'submission': submission
    })


@login_required
@student_only
def student_tests(request):
    group = request.user.profile.group

    tests = list(
        Test.objects.filter(
            group=group
        ).select_related('group').prefetch_related('questions').order_by('-created_at')
    )

    results = TestResult.objects.filter(
        student=request.user,
        test__in=tests
    )

    result_map = {
        result.test_id: result
        for result in results
    }

    for test in tests:
        test.my_result = result_map.get(test.id)
        test.total_questions = test.questions.count()

    return render(request, 'dashboard/student_tests.html', {
        'group': group,
        'tests': tests,
    })


@login_required
@student_only
def solve_test(request, test_id):
    test = get_object_or_404(
        Test.objects.prefetch_related('questions'),
        id=test_id,
        group=request.user.profile.group
    )

    old_result = TestResult.objects.filter(
        test=test,
        student=request.user
    ).prefetch_related('answers').first()

    questions = list(test.questions.all())

    if request.method == 'POST':
        if old_result:
            messages.warning(request, "Siz bu testni oldin yechgansiz!")
            return redirect('dashboard:student_tests')

        total_questions = len(questions)
        correct_count = 0

        result = TestResult.objects.create(
            test=test,
            student=request.user,
            total_questions=total_questions,
            correct_count=0,
        )

        for question in questions:
            selected = request.POST.get(f'answer_{question.id}', '')
            is_correct = selected == question.correct_answer

            if is_correct:
                correct_count += 1

            TestAnswer.objects.create(
                result=result,
                question=question,
                selected_answer=selected,
                is_correct=is_correct
            )

        result.correct_count = correct_count
        result.is_correct = correct_count == total_questions

        if questions:
            first_answer = result.answers.first()
            if first_answer:
                result.selected_answer = first_answer.selected_answer

        result.save()

        messages.success(request, "Test javobi yuborildi!")
        return redirect('dashboard:student_tests')

    answer_map = {}

    if old_result:
        answer_map = {
            answer.question_id: answer
            for answer in old_result.answers.all()
        }

        for question in questions:
            question.my_answer = answer_map.get(question.id)

    return render(request, 'dashboard/solve_test.html', {
        'test': test,
        'questions': questions,
        'old_result': old_result,
    })


@login_required
@student_only
@login_required
@student_only
def student_cases(request):
    group = request.user.profile.group

    if not group:
        return render(request, 'dashboard/student_cases.html', {
            'group': None,
            'cases': [],
        })

    cases = list(
        CaseStudy.objects.filter(
            group=group,
            is_published=True
        ).select_related('group').order_by('-created_at')
    )

    submissions = CaseSubmission.objects.filter(
        student=request.user,
        case__in=cases
    )

    submission_map = {
        submission.case_id: submission
        for submission in submissions
    }

    for case in cases:
        case.my_submission = submission_map.get(case.id)

    return render(request, 'dashboard/student_cases.html', {
        'group': group,
        'cases': cases,
    })
@login_required
@student_only
def solve_case(request, case_id):
    case = get_object_or_404(
        CaseStudy,
        id=case_id,
        group=request.user.profile.group,
        is_published=True
    )

    old_submission = CaseSubmission.objects.filter(
        case=case,
        student=request.user
    ).first()

    if old_submission:
        messages.warning(request, "Siz bu case studyga allaqachon javob yuborgansiz!")
        return redirect('dashboard:student_cases')

    if request.method == 'POST':
        answer = request.POST.get('answer') or ''

        CaseSubmission.objects.create(
            case=case,
            student=request.user,
            answer=answer
        )

        messages.success(request, "Case javobi yuborildi!")
        return redirect('dashboard:student_cases')

    return render(request, 'dashboard/solve_case.html', {
        'case': case,
        'old_submission': old_submission
    })