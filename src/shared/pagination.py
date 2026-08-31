def get_page_offset(page: int, page_size: int) -> int:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1
    return (page - 1) * page_size