from .binary import encode_binary
from .commander import encode_commander
from .pairwise import encode_pairwise
from .product import encode_product
from .sequential import encode_sequential

AMO_METHODS = {
    "pairwise": encode_pairwise,
    "binary": encode_binary,
    "sequential": encode_sequential,
    "commander": encode_commander,
    "product": encode_product,
}