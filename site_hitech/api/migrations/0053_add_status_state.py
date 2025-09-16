from django.db import migrations, models

class Migration(migrations.Migration):
	dependencies = [
		('api', '0052_add_allowed_roles_state'),
	]

	operations = [
		migrations.SeparateDatabaseAndState(
			state_operations=[
				migrations.AddField(
					model_name='document',
					name='status',
					field=models.CharField(max_length=20, default='published', blank=True),
				),
			],
			database_operations=[],
		),
	] 