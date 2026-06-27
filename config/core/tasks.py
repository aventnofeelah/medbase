from datetime import timedelta
from django.utils import timezone
from django.core.files.storage import default_storage
from huey.contrib.djhuey import periodic_task
from huey import crontab

@periodic_task(crontab(minute='0', hour='*/12'))
def clear_expired_tmp_files():
    """
    Асинхронная задача для очистки старых файлов из папки tmp/
    """
    target_dir = 'tmp'
    
    if not default_storage.exists(target_dir):
        return

    directories, files = default_storage.listdir(target_dir)
    
    now = timezone.now()
    expiration_threshold = now - timedelta(hours=1)

    deleted_count = 0

    for filename in files:
        file_path = f"{target_dir}/{filename}"
        
        try:
            modified_time = default_storage.get_modified_time(file_path)
            
            if modified_time < expiration_threshold:
                default_storage.delete(file_path)
                deleted_count += 1
        except Exception as e:
            print(f"Ошибка при удалении файла {file_path}: {e}")

    print(f"Очистка tmp завершена. Удалено файлов: {deleted_count}")