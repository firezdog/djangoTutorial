import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """ was_published_recently() should return false for questions still scheduled to be published """
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = future_time)
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_recently_with_recently_published_question(self):
        """ was_published_recently() should return true for questions recently published. """
        present_time = timezone.now() - timezone.timedelta(hours=23,minutes=59,seconds=59)
        present_question = Question(pub_date = present_time)
        self.assertIs(present_question.was_published_recently(),True)

    def test_was_published_recently_with_previously_published_question(self):
        """ was_published_recently() should return false for questions published in the past. """
        past_time = timezone.now() - timezone.timedelta(days=1, seconds=1)
        past_question = Question(pub_date = past_time)
        self.assertIs(past_question.was_published_recently(),False)

def create_question(question_text,days):
    """ Create question with given text to be published <days> days from now """
    time = timezone.now() + timezone.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_past_questions(self):
        """
        Questions from the past should be displayed
        """
        create_question("Past question.", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_questions(self):
        """
        Questions for the future should not be displayed
        """
        create_question("Future question.", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )


    def test_future_question_and_past_question(self):
        """
        If both past and future questions exist, only past are displayed
        """
        create_question("Past question.", -30)
        create_question("Future question.", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
    
    def test_two_past_questions(self):
        """
        If only past questions exist, past questions are still displayed
        """
        create_question("A", -1)
        create_question("B", -2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: A>', '<Question: B>']
        )

class QuestionDetailsViewTests(TestCase):
    def test_future_questions(self):
        """
        Detail view for future questions = 404
        """
        future_question = create_question("A",1)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_questions(self):
        """
        Detail view for past questions displays question text
        """
        past_question = create_question("A",-1)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response,past_question.question_text)