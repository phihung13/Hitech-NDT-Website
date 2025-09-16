from django.db import migrations, models

class Migration(migrations.Migration):
	dependencies = [
		('api', '0050_merge_20250915_1116'),
	]

	operations = [
		migrations.SeparateDatabaseAndState(
			state_operations=[
				migrations.AddField(
					model_name='document',
					name='access_level',
					field=models.CharField(max_length=20, default='public', blank=True),
				),
			],
			database_operations=[],
		),
	] 