cdef extern from "Python.h":
    object PyString_FromStringAndSize(char *s, int len)

cdef extern from "uuid/uuid.h":
   ctypedef char uuid_t[16]

   void uuid_generate(uuid_t out)
   void uuid_unparse(uuid_t uu, char *out)

   int uuid_parse(char *instr, uuid_t out)

#   time_t uuid_time(uuid_t uu, struct timeval *ret_tv)
#   int uuid_type(uuid_t uu)
#   int uuid_variant(uuid_t uu)

def generate_uuid():
   cdef uuid_t uuid
   cdef char out[37]
   uuid_generate(uuid)
   uuid_unparse(uuid, out)
   return out

#def generate_uuid_bytes():
#   cdef uuid_t uuid
#   uuid_generate(uuid)   
#   return PyString_FromStringAndSize(uuid, 16)

def parse_uuid(char *uuid_str):
   cdef uuid_t out
   if uuid_str is None:
      return None

   if uuid_parse(uuid_str, out) == 0:
      return out
   else:
      return None

#
# TODO: this needs to be rewritten
# I don't (yet) know how in pyrex to allow me to accept
# full python strings with nulls and handle the conversion
# based on length (16) instead of looking for a null.
#

#def unparse_uuid(uuid_t bytes):
#   if bytes is None:
#      return None
#   cdef char out[37]
#   uuid_unparse(bytes, out)
#   return out
