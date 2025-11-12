"""
Service para gerenciar fórum
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_
from app.models.forum_post import ForumPost
from app.models.forum_comment import ForumComment
from typing import List, Optional

class ForumService:
    @staticmethod
    def create_post(
        db: Session,
        user_id: int,
        post_data: dict
    ) -> ForumPost:
        """Criar post no fórum"""
        post = ForumPost(user_id=user_id, **post_data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def get_post_by_id(
        db: Session,
        post_id: int,
        increment_views: bool = False
    ) -> Optional[ForumPost]:
        """Obter post por ID"""
        post = db.query(ForumPost).options(
            joinedload(ForumPost.user)
        ).filter(ForumPost.id == post_id).first()
        
        if post and increment_views:
            post.views += 1
            db.commit()
            db.refresh(post)
        
        return post
    
    @staticmethod
    def list_posts(
        db: Session,
        category: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[ForumPost]:
        """Listar posts"""
        query = db.query(ForumPost).options(
            joinedload(ForumPost.user)
        )
        
        if category:
            query = query.filter(ForumPost.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    ForumPost.title.ilike(search_term),
                    ForumPost.content.ilike(search_term)
                )
            )
        
        return query.order_by(desc(ForumPost.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
    
    @staticmethod
    def update_post(
        db: Session,
        post: ForumPost,
        update_data: dict
    ) -> ForumPost:
        """Atualizar post"""
        for field, value in update_data.items():
            setattr(post, field, value)
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def delete_post(db: Session, post_id: int, user_id: int) -> bool:
        """Deletar post"""
        post = db.query(ForumPost).filter(
            ForumPost.id == post_id,
            ForumPost.user_id == user_id
        ).first()
        
        if not post:
            return False
        
        db.delete(post)
        db.commit()
        return True
    
    @staticmethod
    def create_comment(
        db: Session,
        post_id: int,
        user_id: int,
        comment_data: dict
    ) -> ForumComment:
        """Criar comentário"""
        comment = ForumComment(post_id=post_id, user_id=user_id, **comment_data)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    
    @staticmethod
    def get_comments_by_post(
        db: Session,
        post_id: int
    ) -> List[ForumComment]:
        """Obter comentários de um post"""
        return db.query(ForumComment).options(
            joinedload(ForumComment.user)
        ).filter(
            ForumComment.post_id == post_id
        ).order_by(ForumComment.created_at.asc()).all()
    
    @staticmethod
    def get_comments_count(db: Session, post_id: int) -> int:
        """Contar comentários de um post"""
        return db.query(func.count(ForumComment.id)).filter(
            ForumComment.post_id == post_id
        ).scalar()

