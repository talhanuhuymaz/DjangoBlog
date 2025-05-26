from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Post, Profile, Comment, Notification

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('date_posted',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'total_likes', 'total_comments', 'has_image')
    list_filter = ('date_posted', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('date_posted', 'total_likes')
    inlines = [CommentInline]
    date_hierarchy = 'date_posted'

    def total_comments(self, obj):
        return obj.comments.count()
    total_comments.short_description = 'Comments'

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_avatar', 'followers_count', 'following_count')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('following',)

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 50%;" />', obj.avatar.url)
        return "No avatar"
    display_avatar.short_description = 'Avatar'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'author', 'post_link', 'date_posted')
    list_filter = ('date_posted', 'author')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('date_posted',)

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

    def post_link(self, obj):
        url = reverse('admin:blog_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_link.short_description = 'Post'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False  # Notifications should only be created through the application

# Customize admin site
admin.site.site_header = 'BlogSpace Admin'
admin.site.site_title = 'BlogSpace Admin Portal'
admin.site.index_title = 'Welcome to BlogSpace Admin Portal'
