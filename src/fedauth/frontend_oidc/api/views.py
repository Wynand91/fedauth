from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from mozilla_django_oidc.views import get_next_url

from fedauth.frontend_oidc.api.serializers import LoginSerializer, TokenExchangeSerializer

url_validator = URLValidator()


class OidcLoginView(CreateAPIView):
    """
    This view is used for when you have a frontend app that requires OIDC login.
    The view constructs the idP url and returns it to the frontend.
    The post request payload determines whether it's a federated login (username submitted), or a normal idP login (e.g. user clicked "log in with Facebook")
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @staticmethod
    def validate_url_parameters(request):
        """
        The frontend should be sending a success (next) url and a fail (fail) url parameter
        """
        url_success = get_next_url(request, 'next')
        url_fail = get_next_url(request, 'fail')
        if not url_success or not url_fail:
            raise ValidationError("Missing 'next' and/or 'fail' url parameters")

        try:
            url_validator(url_success)
            url_validator(url_fail)
        except DjangoValidationError:
            raise ValidationError("Invalid 'next' or 'success' url")

        # we need to add urls to session, so that callback knows where to redirect to.
        request.session['next'] = url_success
        request.session['fail'] = url_fail

    def create(self, request, *args, **kwargs):
        self.validate_url_parameters(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'auth_url': serializer.validated_data['auth_url']})


class TokenExchangeView(CreateAPIView):
    """
    After successful authentication via OIDC (frontend flow), a unique code is returned to the
    frontend (see callback view).
    The unique code can be exchanged for jwt tokens using this view.
    """
    serializer_class = TokenExchangeSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jwt_tokens = serializer.validated_data['tokens']
        return Response(jwt_tokens)
