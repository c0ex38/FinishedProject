import re
from .models import Hashtag, PostHashtag

def extract_hashtags(text):
    """
    Metinden hashtag'leri çıkarır ve liste olarak döndürür
    """
    if not text:
        return []
    
    # Hashtag regex: # işareti ve ardından alfanümerik karakterler
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text)
    
    # Benzersiz hashtag'leri döndür
    return list(set([tag.lower() for tag in hashtags]))

def process_post_hashtags(post):
    """
    Post içeriğindeki hashtag'leri işler ve veritabanına kaydeder
    """
    # Post içeriğinden hashtag'leri çıkar
    content_hashtags = extract_hashtags(post.content)
    title_hashtags = extract_hashtags(post.title)
    
    # Tüm hashtag'leri birleştir
    all_hashtags = list(set(content_hashtags + title_hashtags))
    
    # Mevcut hashtag'leri temizle
    PostHashtag.objects.filter(post=post).delete()
    
    # Yeni hashtag'leri ekle
    for tag_name in all_hashtags:
        # Hashtag'i bul veya oluştur
        hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
        
        # Post ile hashtag'i ilişkilendir
        PostHashtag.objects.create(post=post, hashtag=hashtag)
        
        # Hashtag sayısını güncelle
        hashtag.post_count = PostHashtag.objects.filter(hashtag=hashtag).count()
        hashtag.save()