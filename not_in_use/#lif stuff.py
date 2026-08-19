#lif stuff

if str(suffix)=='.lif': 
get_lifs= LifFile(source)
reader_platform = [i for i in get_lifs.get_iter_image()]

#with reader_platform as ims_thisframe:
for lif_objects in reader_platform:
ims_thisframe=lif_objects.getframe
        