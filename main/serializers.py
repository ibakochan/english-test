from rest_framework import serializers
import base64
from .models import School, Classroom, Test, Question, Option, UserTestSubmission, TestRecords
from accounts.models import CustomUser, Sessions
from .forms import SchoolCreateForm, ClassroomCreateForm, TestCreateForm, QuestionCreateForm, OptionCreateForm, TestSubmissionForm, ConnectTestForm


class SchoolSerializer(serializers.ModelSerializer):
    school_picture = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = '__all__'

    def get_school_picture(self, obj):
        if obj.school_picture:
            return base64.b64encode(obj.school_picture).decode('utf-8')
        return None

class ClassroomSerializer(serializers.ModelSerializer):
    classroom_picture = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = '__all__'

    def get_classroom_picture(self, obj):
        if obj.classroom_picture:
            return base64.b64encode(obj.classroom_picture).decode('utf-8')
        return None

class TestSerializer(serializers.ModelSerializer):
    test_picture = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = '__all__'

    def get_test_picture(self, obj):
        if obj.test_picture:
            return base64.b64encode(obj.test_picture).decode('utf-8')
        return None

class QuestionSerializer(serializers.ModelSerializer):
    question_picture = serializers.SerializerMethodField()
    question_sound = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = '__all__'

    def get_question_picture(self, obj):
        if obj.question_picture:
            return base64.b64encode(obj.question_picture).decode('utf-8')
        return None

    def get_question_sound(self, obj):
        if obj.question_sound:
            return base64.b64encode(obj.question_sound).decode('utf-8')
        return None

class OptionSerializer(serializers.ModelSerializer):
    option_picture = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = '__all__'

    def get_option_picture(self, obj):
        if obj.option_picture:
            return base64.b64encode(obj.option_picture).decode('utf-8')
        return None

class TestRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestRecords
        fields = '__all__'

class SessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sessions
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class ConnectTestFormSerializer(serializers.Serializer):
    # Define the fields for your form here
    pass
