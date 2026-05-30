import enum

from app.extensions import db
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class NotificationType(str, enum.Enum):
    SYSTEM = "system"
    EVENT = "event"
    PAYMENT = "payment"
    CONNECTION = "connection"
    MESSAGE = "message"
    WORKSHOP = "workshop"
    ANNOUNCEMENT = "announcement"
    REMINDER = "reminder"


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.Enum(NotificationType), default=NotificationType.SYSTEM, index=True)
    title = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    metadata_json = db.Column(db.JSON, default=dict)

    user = db.relationship("User", back_populates="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value if self.type else None,
            "title": self.title,
            "message": self.message,
            "link": self.link,
            "is_read": self.is_read,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Community(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "communities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    banner_url = db.Column(db.String(500), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    is_public = db.Column(db.Boolean, default=True)
    member_count = db.Column(db.Integer, default=0)

    owner = db.relationship("User")
    members = db.relationship("CommunityMember", back_populates="community", lazy="dynamic")
    events = db.relationship("Event", back_populates="community", lazy="dynamic")
    posts = db.relationship("Post", back_populates="community", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "avatar_url": self.avatar_url,
            "banner_url": self.banner_url,
            "owner_id": self.owner_id,
            "is_public": self.is_public,
            "member_count": self.member_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CommunityMemberRole(str, enum.Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"


class CommunityMember(TimestampMixin, db.Model):
    __tablename__ = "community_members"

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(
        db.Integer,
        db.ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(db.Enum(CommunityMemberRole), default=CommunityMemberRole.MEMBER)

    community = db.relationship("Community", back_populates="members")
    user = db.relationship("User")

    __table_args__ = (db.UniqueConstraint("community_id", "user_id", name="uq_community_member"),)


class Post(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(
        db.Integer,
        db.ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=True)
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500), nullable=True)
    likes_count = db.Column(db.Integer, default=0)

    community = db.relationship("Community", back_populates="posts")
    author = db.relationship("User")
    comments = db.relationship("Comment", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "community_id": self.community_id,
            "author_id": self.author_id,
            "title": self.title,
            "content": self.content,
            "media_url": self.media_url,
            "likes_count": self.likes_count,
            "comment_count": self.comments.filter_by(is_deleted=False).count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Comment(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)

    post = db.relationship("Post", back_populates="comments")
    author = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "author_id": self.author_id,
            "content": self.content,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
