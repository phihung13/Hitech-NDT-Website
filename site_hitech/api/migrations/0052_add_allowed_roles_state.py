from django.db import migrations, models

class Migration(migrations.Migration):
	dependencies = [
		('api', '0051_add_access_level_state'),
	]

	operations = [
		migrations.SeparateDatabaseAndState(
			state_operations=[
				migrations.AddField(
					model_name='document',
					name='allowed_roles',
					field=models.CharField(max_length=100, default='all', blank=True),
				),
			],
			database_operations=[],
		),
	] 