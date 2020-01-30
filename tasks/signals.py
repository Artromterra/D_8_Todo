from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from tasks.models import TodoItem, Category, Priority
from collections import Counter

def print_signal_info(sender, instance, action, model, **kwargs):
	print()
	print(f'sender = {sender}')
	print(f'instance = {instance}')
	print(f'action = {action}')
	print(f'model = {model.__name__}')
	print(f'kwargs')
	for key, value in kwargs.items():
		print(f'key = {key}, value = {value}')
	print()

@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):
	if action != "post_add":
		return

	for cat in instance.category.all():
		slug = cat.slug

		new_count = 0
		for task in TodoItem.objects.all():
			new_count += task.category.filter(slug=slug).count()
		Category.objects.filter(slug=slug).update(todos_count=new_count)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, **kwargs):
	if action != "post_remove":
		return

	cat_counter = Counter()
	for cat in Category.objects.all():
		cat_counter[cat.slug] = 0
	for t in TodoItem.objects.all():
		for cat in t.category.all():
			cat_counter[cat.slug] += 1

	for slug, new_count in cat_counter.items():
		Category.objects.filter(slug=slug).update(todos_count=new_count)

@receiver(post_save, sender=TodoItem)
def priority_save(sender, instance, action="post_save", model=TodoItem, **kwargs):
	print_signal_info(sender, instance, action, model, **kwargs)

	for prior in Priority.objects.all():
		prior.count = prior.tasks.count()
		prior.save()

@receiver(post_delete, sender=TodoItem)
def priority_delete(sender, instance, action="post_delete", model=TodoItem, **kwargs):
	print_signal_info(sender, instance, action, model, **kwargs)

	for prior in Priority.objects.all():
		prior.count = prior.tasks.count()
		prior.save()