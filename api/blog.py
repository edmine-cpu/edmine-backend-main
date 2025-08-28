from fastapi import APIRouter, HTTPException
from models.actions import BlogArticle
from typing import List, Optional

router = APIRouter()

@router.get("/blog/articles")
async def get_blog_articles(lang: str = "uk", limit: int = 10, offset: int = 0):
    """Get published blog articles"""
    if lang not in ['uk', 'en', 'pl', 'fr', 'de']:
        raise HTTPException(status_code=400, detail="Unsupported language")
    
    try:
        articles = await BlogArticle.filter(
            is_published=True
        ).order_by('-created_at').offset(offset).limit(limit).prefetch_related('author')
        
        result = []
        for article in articles:
            # Get title and description for the specified language
            title = getattr(article, f'title_{lang}', article.title_uk)
            description = getattr(article, f'description_{lang}', article.description_uk)
            slug = getattr(article, f'slug_{lang}', article.slug_uk)
            
            result.append({
                "id": article.id,
                "title": title,
                "description": description,
                "slug": slug,
                "featured_image": article.featured_image,
                "author_name": article.author.name if article.author else "Unknown",
                "created_at": article.created_at.isoformat(),
                "updated_at": article.updated_at.isoformat()
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")

@router.get("/blog/articles/{article_id}")
async def get_blog_article(article_id: int, lang: str = "uk"):
    """Get specific blog article"""
    if lang not in ['uk', 'en', 'pl', 'fr', 'de']:
        raise HTTPException(status_code=400, detail="Unsupported language")
    
    try:
        article = await BlogArticle.get_or_none(id=article_id, is_published=True).prefetch_related('author')
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get content for the specified language
        title = getattr(article, f'title_{lang}', article.title_uk)
        content = getattr(article, f'content_{lang}', article.content_uk)
        description = getattr(article, f'description_{lang}', article.description_uk)
        keywords = getattr(article, f'keywords_{lang}', article.keywords_uk)
        slug = getattr(article, f'slug_{lang}', article.slug_uk)
        
        return {
            "id": article.id,
            "title": title,
            "content": content,
            "description": description,
            "keywords": keywords,
            "slug": slug,
            "featured_image": article.featured_image,
            "author_name": article.author.name if article.author else "Unknown",
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching article: {str(e)}")
