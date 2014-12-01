from __future__ import unicode_literals

from nap import http


class JsonResponseMixin(JsonMixin):
    response_class = http.HttpResponse

    def render_to_response(self, context, **response_kwargs):
        response_class = response_kwargs.pop('response_class', self.response_class)

        content = self.dumps(context)
        response_kwargs.setdefault('content_type', self.CONTENT_TYPES[0])

        return response_class(content, **response_kwargs)


class SingleObjectMixin(object):

    def get_object_list(self):
        raise NotImplementedError

    def get_object(self, object_id):
        raise NotImplementedError

    def get_serialiser(self):
        return self.serialiser

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(kwargs['object_id'])

        serialiser = self.get_serialiser()
        serialiser_kwargs = self.get_serialiser_kwargs()

        return self.render_to_response(
            serialiser.object_deflate(self.object, **serialiser_kwargs)
        )

    def post(self, request, *args, **kwargs):
        data = self.get_request_data(None)
        if data is None:
            raise http.BadRequest()

        serialiser = self.get_serialiser()
        serialiser_kwargs = self.get_serialiser_kwargs()

        try:
            self.object = serialiser.object_inflate(data, **kwargs)
        except ValidationError as ve:
            return self.validate_failed(data, ve)
        return self.validate_passed(self.object, data=data)

