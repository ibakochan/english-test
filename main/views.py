from django.shortcuts import render
from django.views import View
from accounts.models import CustomUser, Sessions
from django.http import JsonResponse
from django import forms
from accounts.forms import CustomUserCreationForm
from .models import School, Classroom, Test, Question, Option, UserTestSubmission, TestRecords
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.db.models import Count
from random import shuffle
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import json
import base64
from django.db.models.query import QuerySet
from rest_framework import serializers
from .serializers import (SchoolSerializer, ClassroomSerializer, TestSerializer, QuestionSerializer, OptionSerializer,
                          TestRecordsSerializer, SessionsSerializer, CustomUserSerializer, ConnectTestFormSerializer)
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth.hashers import check_password
from .forms import SchoolCreateForm, ClassroomCreateForm, TestCreateForm, QuestionCreateForm, OptionCreateForm, TestSubmissionForm, ConnectTestForm
from .owner import OwnerDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect









def remove_digits_from_end(string, num_digits):
    """
    Remove the specified number of digits from the end of the string.
    """
    return string[:-num_digits]





class TestClassroomView(View):
    def post(self, request, pk):
        test = Test.objects.get(pk=pk)
        connect_form = ConnectTestForm(request.POST, instance=test)

        if connect_form.is_valid():
            connect_form.save()  # save() handles the ManyToManyField correctly
            return redirect('main:profile')


class ProfilePageView(LoginRequiredMixin, View):


    template_name = 'main/test.html'

    def get(self, request):

        test_records = TestRecords.objects.filter(user=request.user)
        account_sessions = Sessions.objects.filter(user=request.user)

        questions = list(Question.objects.all())
        shuffle(questions)

        options = list(Option.objects.all())
        options.reverse()

        test_ids = [session.number for session in account_sessions]
        classrooms = Classroom.objects.all()

        tests = Test.objects.all()
        session_tests = Test.objects.filter(pk__in=test_ids)



        connect_form = ConnectTestForm()

        return render(request, self.template_name, {
                'users': CustomUser.objects.all(),
                'schools': School.objects.all(),
                'classrooms': classrooms,
                'tests': tests,
                'questions': questions,
                'options': options,
                'school_form': SchoolCreateForm(),
                'test_form': TestCreateForm(),
                'question_form': QuestionCreateForm(),
                'option_form': OptionCreateForm(),
                'classroom_form': ClassroomCreateForm(),
                'signup_form': CustomUserCreationForm(),
                'test_records': test_records,
                'account_sessions': account_sessions,
                'session_tests': session_tests,
                'connect_form': connect_form,
            })

    def post(self, request):
        school_name = request.POST.get('school_name')
        school_password = request.POST.get('school_password')
        classroom_name = request.POST.get('classroom_name')
        classroom_password = request.POST.get('classroom_password')


        tests = Test.objects.all()
        user_test_submissions = UserTestSubmission.objects.filter(user=request.user, test__in=tests)

        test_records = TestRecords.objects.filter(user=request.user)
        account_sessions = Sessions.objects.filter(user=request.user)
        test_ids = [session.number for session in account_sessions]

        session_tests = Test.objects.filter(pk__in=test_ids)




        test_submission_form = TestSubmissionForm()
        connect_form = ConnectTestForm()

        options = list(Option.objects.all())
        shuffle(options)
        questions = list(Question.objects.all())
        shuffle(questions)

        modified_options = []

        for option in options:
            pk_length = len(str(option.pk))
            option_name = remove_digits_from_end(option.name, pk_length)
            modified_options.append({'option': option, 'option_name': option_name})

        signup_form = CustomUserCreationForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            login(request, user)


        return render(request, self.template_name, {
            'modified_options': modified_options,
            'users': CustomUser.objects.all(),
            'schools': School.objects.all(),
            'classrooms': Classroom.objects.all(),
            'questions': questions,
            'options': options,
            'school_form': SchoolCreateForm(),
            'test_form': TestCreateForm(),
            'question_form': QuestionCreateForm(),
            'option_form': OptionCreateForm(),
            'classroom_form': ClassroomCreateForm(),
            'school_name': school_name,
            'school_password': school_password,
            'classroom_name': classroom_name,
            'classroom_password': classroom_password,
            'tests': tests,
            'test_submission_form': test_submission_form,
            'signup_form': signup_form,
            'user_test_submissions': user_test_submissions,
            'connect_form': connect_form,
            'test_records': test_records,
            'account_sessions': account_sessions,
            'session_tests': session_tests,
        })


class SignUpView(View):
    def post(self, request):
        signup_form = CustomUserCreationForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            login(request, user)
            return redirect('/')



class AccountDeleteView(OwnerDeleteView):
    # Using the OwnerDeleteView I got from dj4e to delete accounts.

    model = CustomUser
    template_name = 'main/test.html'

    def get_success_url(self):
        current_user_id = self.request.user.id
        return reverse('main:profile', kwargs={'user_id': current_user_id})



class SchoolCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = SchoolCreateForm(request.POST, request.FILES or None)
        if form.is_valid():
            school = form.save(commit=False)
            school.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)



class ClassroomCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        form = ClassroomCreateForm(request.POST, request.FILES or None)
        school = get_object_or_404(School, pk=pk)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.school = school
            classroom.teacher=request.user
            classroom.save()
            response_data = {'success': True, 'school_pk': school.pk}
            return JsonResponse(response_data)
        else:
            response_data = {'success': False, 'errors': form.errors, 'school_pk': school.pk}
            return JsonResponse(response_data, status=400)


class TestCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        form = TestCreateForm(request.POST, request.FILES or None)
        classroom = get_object_or_404(Classroom, pk=pk)
        if form.is_valid():
            test = form.save(commit=False)
            test.save()
            test.classroom.add(classroom)
            response_data = {'success': True, 'classroom_pk': classroom.pk}
            return JsonResponse(response_data)
        else:
            response_data = {'success': False, 'errors': form.errors, 'classroom_pk': classroom.pk}
            return JsonResponse(response_data, status=400)



class QuestionCreateView(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        form = QuestionCreateForm(request.POST, request.FILES or None)
        test = get_object_or_404(Test, pk=pk)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()

            total_questions = Question.objects.filter(test=test).count()
            test.total_questions = total_questions
            test.save()

            test.total_questions == total_questions


            response_data = {'success': True, 'test_pk': test.pk, 'pk': question.pk, 'name': question.name, 'test_name': test.name}
            return JsonResponse(response_data)
        else:
            response_data = {'success': False, 'errors': form.errors, 'test_name': test.name, 'test_pk': test.pk}
            return JsonResponse(response_data, status=400)


class QuestionDeleteView(LoginRequiredMixin, View):
    # For deleting items within the ToDoList.

    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        test = question.test


        question.delete()

        total_questions = Question.objects.filter(test=test).count()
        test.total_questions = total_questions
        test.save()


        response_data = {'status': 'success', 'pk': pk}
        return JsonResponse(response_data)


class OptionCreateView(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        question = get_object_or_404(Question, pk=pk)

        form = OptionCreateForm(request.POST, request.FILES or None)
        if form.is_valid():
            option = form.save(commit=False)
            option.question = question
            option.save()
            response_data = {'success': True, 'pk': option.pk, 'name': option.name}
            return JsonResponse(response_data)
        else:
            response_data = {'success': False, 'errors': form.errors, 'question_pk': question.pk}
            return JsonResponse(response_data, status=400)

class OptionDeleteView(LoginRequiredMixin, View):
    # For deleting items within the ToDoList.

    def post(self, request, pk):
        option = get_object_or_404(Option, pk=pk)

        option.delete()

        response_data = {'status': 'success', 'pk': pk}
        return JsonResponse(response_data)



def school_stream_file(request, pk):

    school = get_object_or_404(School, id=pk)
    response = HttpResponse()
    response['Content-Type'] = school.school_content_type
    response['Content-Length'] = len(school.school_picture)
    response.write(school.school_picture)
    return response


def classroom_stream_file(request, pk):

    classroom = get_object_or_404(Classroom, id=pk)
    response = HttpResponse()
    response['Content-Type'] = classroom.classroom_content_type
    response['Content-Length'] = len(classroom.classroom_picture)
    response.write(classroom.classroom_picture)
    return response


def test_stream_file(request, pk):

    test = get_object_or_404(Test, id=pk)
    response = HttpResponse()
    response['Content-Type'] = test.test_content_type
    response['Content-Length'] = len(test.test_picture)
    response.write(test.test_picture)
    return response


def question_stream_file(request, pk):

    question = get_object_or_404(Question, id=pk)
    response = HttpResponse()
    response['Content-Type'] = question.question_content_type
    response['Content-Length'] = len(question.question_picture)
    response.write(question.question_picture)
    return response

def question_sound_file(request, pk):

    question = get_object_or_404(Question, id=pk)
    response = HttpResponse()
    response['Content-Type'] = question.question_sound_content_type
    response['Content-Length'] = len(question.question_sound)
    response.write(question.question_sound)
    return response


def option_stream_file(request, pk):

    option = get_object_or_404(Option, id=pk)
    response = HttpResponse()
    response['Content-Type'] = option.option_content_type
    response['Content-Length'] = len(option.option_picture)
    response.write(option.option_picture)
    return response



class TestAnswerView(LoginRequiredMixin, View):

    def post(self, request, pk):
        form = TestSubmissionForm(request.POST)

        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.test_id = pk
            submission.question=submission.selected_option.question


            score = 0
            if submission.selected_option.is_correct:
                score += 1
                submission.score = score
                message = 'Correct answer'
            else:
                correct_option = Option.objects.filter(question=submission.selected_option.question, is_correct=True).first()
                num_digits = len(str(submission.selected_option.pk))
                # Remove the same number of letters from the end of the option name
                modified_option_name = correct_option.name[:-num_digits]
                message = f'あまい！ Correct answer = {modified_option_name}'

            submission.save()


            response_data = {'success': True, 'message': message}
            return JsonResponse(response_data)
        else:
            response_data = {'success': False, 'errors': form.errors}
            return JsonResponse(response_data, status=400)


class TestRecordView(View):
    def post(self, request, pk):
        # Retrieve the Test instance
        test = get_object_or_404(Test, pk=pk)
        total_questions = test.total_questions

        TestRecordView.activation_counter += 1
        group_id = TestRecordView.activation_counter

        account_sessions = Sessions.objects.create(number=test.pk, user=request.user)

        # Retrieve all UserTestSubmission instances related to the request user and the specified test
        user_test_submissions = UserTestSubmission.objects.filter(user=request.user, test=test)

        # List to store the created TestRecord IDs
        test_record_ids = []

        # Iterate over each UserTestSubmission instance
        for user_test_submission in user_test_submissions:
            # Access question name and selected option from UserTestSubmission
            question_name = str(user_test_submission.selected_option.question.name)
            selected_option_name = str(user_test_submission.selected_option.name)
            recorded_score = int(user_test_submission.score)  # Convert score to an integer
            question = user_test_submission.question

            # Create a TestRecord instance
            test_record = TestRecords.objects.create(
                user=request.user,  # Set the user directly from request.user
                test=test,
                question=question,
                question_name=question_name,
                selected_option_name=selected_option_name,
                recorded_score=recorded_score,
                group_id=group_id,
                account_sessions=account_sessions
            )

            # Append the created TestRecord ID to the list
            test_record_ids.append(test_record.id)


        total_score = sum(user_test_submission.score for user_test_submission in user_test_submissions)
        total_score = int(total_score)

        # Create a TestRecord instance to store the total score for the test
        total_score_record = TestRecords.objects.create(
            user=request.user,
            test=test,
            total_recorded_score=total_score,
            group_id=group_id,
            account_sessions=account_sessions
        )

        # Append the created TestRecord ID to the list
        test_record_ids.append(total_score_record.id)
        # Delete all existing UserTestSubmission instances related to the request user and the specified test
        user_test_submissions.delete()

        # Prepare JSON response data
        response_data = {
            'success': True,
            'message': f'Total score: {total_score}/{total_questions}!',
            'test_record_ids': test_record_ids
        }

        # Return JSON response
        return JsonResponse(response_data)
TestRecordView.activation_counter = 0


class TestsubmissionsDeleteView(View):
    def post(self, request):
        # Retrieve the Test instance

        # Retrieve all UserTestSubmission instances related to the request user and the specified test
        user_test_submissions = UserTestSubmission.objects.filter(user=request.user)


        user_test_submissions.delete()



        response_data = {
            'success': True,
        }

        # Return JSON response
        return JsonResponse(response_data)