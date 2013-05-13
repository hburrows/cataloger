# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Graph'
        db.create_table(u'api_graph', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('graph_uri', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal(u'api', ['Graph'])

        # Adding model 'UserProfile'
        db.create_table(u'api_userprofile', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('schema', self.gf('django.db.models.fields.TextField')(max_length=128, null=True)),
        ))
        db.send_create_signal(u'api', ['UserProfile'])

        # Adding M2M table for field graphs on 'UserProfile'
        db.create_table(u'api_userprofile_graphs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'api.userprofile'], null=False)),
            ('graph', models.ForeignKey(orm[u'api.graph'], null=False))
        ))
        db.create_unique(u'api_userprofile_graphs', ['userprofile_id', 'graph_id'])

        # Adding model 'Subject'
        db.create_table(u'api_subject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'api', ['Subject'])

        # Adding model 'Entry'
        db.create_table(u'api_entry', (
            (u'subject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['api.Subject'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'api', ['Entry'])

        # Adding model 'Image'
        db.create_table(u'api_image', (
            (u'subject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['api.Subject'], unique=True, primary_key=True)),
            ('original_width', self.gf('django.db.models.fields.IntegerField')()),
            ('original_height', self.gf('django.db.models.fields.IntegerField')()),
            ('original', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('thumbnail_width', self.gf('django.db.models.fields.IntegerField')()),
            ('thumbnail_height', self.gf('django.db.models.fields.IntegerField')()),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('image_url', self.gf('django.db.models.fields.TextField')(max_length=255)),
        ))
        db.send_create_signal(u'api', ['Image'])


    def backwards(self, orm):
        # Deleting model 'Graph'
        db.delete_table(u'api_graph')

        # Deleting model 'UserProfile'
        db.delete_table(u'api_userprofile')

        # Removing M2M table for field graphs on 'UserProfile'
        db.delete_table('api_userprofile_graphs')

        # Deleting model 'Subject'
        db.delete_table(u'api_subject')

        # Deleting model 'Entry'
        db.delete_table(u'api_entry')

        # Deleting model 'Image'
        db.delete_table(u'api_image')


    models = {
        u'api.entry': {
            'Meta': {'object_name': 'Entry', '_ormbases': [u'api.Subject']},
            u'subject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['api.Subject']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'api.graph': {
            'Meta': {'object_name': 'Graph'},
            'graph_uri': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'api.image': {
            'Meta': {'object_name': 'Image', '_ormbases': [u'api.Subject']},
            'image_url': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'original_height': ('django.db.models.fields.IntegerField', [], {}),
            'original_width': ('django.db.models.fields.IntegerField', [], {}),
            u'subject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['api.Subject']", 'unique': 'True', 'primary_key': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'thumbnail_height': ('django.db.models.fields.IntegerField', [], {}),
            'thumbnail_width': ('django.db.models.fields.IntegerField', [], {})
        },
        u'api.subject': {
            'Meta': {'object_name': 'Subject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'api.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'graphs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['api.Graph']", 'symmetrical': 'False'}),
            'schema': ('django.db.models.fields.TextField', [], {'max_length': '128', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api']