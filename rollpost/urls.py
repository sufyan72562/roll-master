from django.urls import path
from rollpost.views import Upload, Uploadthread, UpdateViews, LikeView, GetLikersView, UploadComment, ReplyComment \
    , CommentView, GetPostView, DeletePostVIew, DeleteReplyCommentVIew, DeleteCommentVIew, ReportAdminView, \
    AllReportAdminView, GetComment, GetReplyComment, UploadVideo

urlpatterns = [
    path('upload/', Upload.as_view(), name="upload"),
    path('upload_video/', UploadVideo.as_view(), name="upload-video"),
    path('uploadthread/', Uploadthread.as_view(), name="upload"),
    path('get-post/<int:id>', GetPostView.as_view(), name="getpost"),
    path('updateviews/<int:id>/', UpdateViews.as_view(), name="updateview"),
    path('like/<int:id>/', LikeView.as_view(), name='like'),
    path('get-likers/<int:id>/', GetLikersView.as_view(), name='getlikers'),
    path('upload-comment/', UploadComment.as_view(), name="uploadcomment"),
    path('reply-comment/', ReplyComment.as_view(), name="replycomment"),
    path('get-comments/<int:id>', CommentView.as_view(), name="getcomment"),
    path('delete-post/<int:id>', DeletePostVIew.as_view(), name="deletepost"),
    path('delete-comment/<int:id>', DeleteCommentVIew.as_view(), name="deletecomment"),
    path('delete-replycomment/<int:id>', DeleteReplyCommentVIew.as_view(), name="deletereplycomment"),
    path('report/', ReportAdminView.as_view(), name="reportadmin"),
    path('allreport/', AllReportAdminView.as_view(), name="allreportadmin"),
    path('getcomment/<int:id>/', GetComment.as_view(), name="getcomment"),
    path('getcommentreply/<int:id>/', GetReplyComment.as_view(), name="getcommentreply")

]
