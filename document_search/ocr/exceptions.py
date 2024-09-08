class DocProcessingException(Exception): ...


class ConvertToImagesError(DocProcessingException):
    def __init__(self):
        super().__init__("Error occurred when converting pdf document to images")


class ExtractTablesError(DocProcessingException):
    def __init__(self):
        super().__init__("Error occurred when extracting tables from page")


class ExtractTextBlockError(DocProcessingException):
    def __init__(self):
        super().__init__("Error occurred when extracting text block from page")


class ExtractImageError(DocProcessingException):
    def __init__(self):
        super().__init__("Error occurred when extracting image from page")
