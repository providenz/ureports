def get_or_create_object(model, *args, **kwargs):
    try:
        obj = model.objects.get(*args, **kwargs)
    except:
        obj = model.objects.create(*args, **kwargs)
        obj.save()
    return obj
