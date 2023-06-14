use FTP to download or upload all files in a single directory from/to a
remote site and directory; this version has been refactored to use classes
and OOP for namespace and a natural structure; I could also structure this
as a download superclass, and an upload subclass which redefines the clean
and transfer methods, but then there is no easy way for another client to
invoke both an upload and download; for the uploadall variant and possibly
others, also make single file upload/download code in orig loops methods;