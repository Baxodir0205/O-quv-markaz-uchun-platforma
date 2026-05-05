from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import CaseStudy, CaseSubmission


def case_list(request):
    cases = CaseStudy.objects.filter(is_published=True)

    context = {
        'cases': cases
    }

    return render(request, 'cases/case_list.html', context)


@login_required
def case_detail(request, slug):
    case = get_object_or_404(CaseStudy, slug=slug, is_published=True)

    existing_submission = CaseSubmission.objects.filter(
        student=request.user,
        case=case
    ).first()

    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip()

        if answer:
            if existing_submission:
                existing_submission.answer = answer
                existing_submission.save()
            else:
                CaseSubmission.objects.create(
                    student=request.user,
                    case=case,
                    answer=answer
                )

                profile = request.user.profile
                profile.xp += case.xp_reward
                profile.coins += case.coin_reward
                profile.save()

            return redirect('case_detail', slug=case.slug)

    context = {
        'case': case,
        'existing_submission': existing_submission,
    }

    return render(request, 'cases/case_detail.html', context)


@login_required
def teacher_submission_detail(request, pk):
    if request.user.profile.role != 'teacher':
        return redirect('dashboard')

    submission = get_object_or_404(
        CaseSubmission.objects.select_related('student', 'case'),
        pk=pk,
        case__teacher=request.user
    )

    if request.method == 'POST':
        score = request.POST.get('score', '0').strip()
        feedback = request.POST.get('feedback', '').strip()

        try:
            score = int(score)
        except ValueError:
            score = 0

        submission.score = score
        submission.feedback = feedback
        submission.save()

        return redirect('teacher_submission_detail', pk=submission.pk)

    context = {
        'submission': submission,
    }

    return render(request, 'cases/teacher_submission_detail.html', context)