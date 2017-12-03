# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Author(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    name = models.TextField()
    pagerank = models.FloatField(blank=True)
    h_index = models.IntegerField(blank=True)

    papers = models.ManyToManyField('Paper', through='PaperAuthor')

    class Meta:
        managed = False
        db_table = 'authors'


class Paper(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    year = models.IntegerField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    event_type = models.TextField(blank=True, null=True)
    pdf_name = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    paper_text = models.TextField(blank=True, null=True)

    authors = models.ManyToManyField(Author, through='PaperAuthor', related_name='authored_papers')
    topics = models.ManyToManyField('Topic', through='PaperTopic')
    suggested_authors = models.ManyToManyField(Author, through='PaperSuggestedAuthor', related_name='author_suggested_for_papers')

    def __str__(self):
        return "{} {}".format(self.id, self.title)

    def get_suggested_papers(self):
        import sqlite3
        conn = sqlite3.connect('data/database.sqlite')
        c = conn.cursor()
        query = "SELECT * FROM suggested_papers WHERE paper_id = {}".format(self.id)
        results_db = c.execute(query)
        results = []
        for r in results_db:
            sp_id = r[2]
            paper = Paper.objects.get(id=sp_id)
            results.append({'paper': paper, 'probability': r[3]})

        return list(results)


    class Meta:
        managed = False
        db_table = 'papers'


class PaperSuggestedAuthor(models.Model):
    id = models.IntegerField(primary_key=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='similar_authors')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='suggested_for_paper')

    class Meta:
        managed = False
        db_table = 'paper_suggested_authors'
        unique_together = ('paper', 'author')


class SuggestedPaper(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='papers')
    suggested_paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='paper_suggested_for_paper')
    probability = models.FloatField()

    class Meta:
        managed = False,
        db_table = 'suggested_papers',
        unique_together = (('paper', 'suggested_paper'),)


class Topic(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'topics'


class PaperTopic(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topics_for')
    probability = models.FloatField()

    class Meta:
        managed = False
        db_table = 'paper_topics'
        unique_together = (('paper', 'topic'),)


class PaperAuthor(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'paper_authors'


class Reference(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    # Related name for the paper is how a paper can get its references.
    # First, it finds itself by finding itself using paper and next finds the references by reference_paper
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='references')
    reference_paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='referenced_by')

    class Meta:
        managed = False
        db_table = 'references'
        unique_together = (('paper', 'reference_paper'),)


class SuggestedAuthor(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='suggested_authors')
    suggested_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='suggested_for')
    similarity = models.FloatField()

    class Meta:
        managed = False
        db_table = 'suggested_authors'
        unique_together = (('author', 'suggested_author'),)


class TopicEvolution(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='evolution')
    year = models.TextField()
    score = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'topic_evolutions'
        unique_together = (('year', 'topic'),)
