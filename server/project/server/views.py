from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Shop, FidelityProgram, Catalogue
from .modelvalidators import (UserSerializer, ShopSerializer, FidelityProgramSerializer, 
                              CashbackProgramSerializer, PointsProgramSerializer, 
                              LevelsProgramSerializer, MembershipProgramSerializer, CatalogueSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint allowing users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class ShopViewSet(viewsets.ModelViewSet):
    """
    API endpoint allowing shops to be viewed or edited.
    """
    queryset = Shop.objects.all().order_by('name')
    serializer_class = ShopSerializer

class FidelityProgramViewSet(viewsets.ModelViewSet):
    """
    API endpoint allowing fidelity programs to be 
    viewed or edited.
    """
    queryset = FidelityProgram.objects.all().order_by('name')
    serializer_class = FidelityProgramSerializer

    # def get_queryset(self):
    #    if self.action == 'pointsprograms':
    #        return FidelityProgram.objects.filter(program_type='PT').order_by('name')
    #    return FidelityProgram.objects.all().order_by('name')

    # def get_serializer_class(self):
    #    if self.action == 'pointsprograms' or self.action == 'create_points_program':
    #        return PointsProgramSerializer
    #    return FidelityProgramSerializer

    @classmethod
    def create_fidelity_program(cls, ptype, request, pk=None):
        if ptype == FidelityProgram.CASHBACK:
            serializer = CashbackProgramSerializer()
        elif ptype == FidelityProgram.POINTS:
            serializer = PointsProgramSerializer()
        elif ptype == FidelityProgram.LEVELS:
            serializer = LevelsProgramSerializer()
        elif ptype == FidelityProgram.MEMBERSHIP:
            serializer = MembershipProgramSerializer()
        else:
            serializer = FidelityProgramSerializer()
        serializer.data = request.data
        serializer.context = {'request': request}
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(
        detail=False,
        methods=['get'],
        url_path=r'byshop/(?P<shop>(\w|\s)+)'
    )
    def get_by_shop(self, request, shop, pk=None):
        try:
            return Response(self.serializer_class(
                FidelityProgram.objects.filter(shop_list__in=[shop]).order_by('name'),
                many=True,
                context={'request': request}).data)
        except FidelityProgram.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False)
    def pointsprograms(self, request, pk=None):
        """
        API endpoint allowing POINTS programs to be
        viewed or edited.
        """
        return Response(PointsProgramSerializer(
            FidelityProgram.objects.filter(program_type=FidelityProgram.POINTS).order_by('name'),
            many=True,
            context={'request': request}).data)

    @action(detail=False)
    def levelsprograms(self, request, pk=None):
        """
        API endpoint allowing LEVELS programs to be
        viewed or edited.
        """
        return Response(LevelsProgramSerializer(
            FidelityProgram.objects.filter(program_type=FidelityProgram.LEVELS).order_by('name'),
            many=True,
            context={'request': request}).data)

    @action(detail=False)
    def membershipprograms(self, request, pk=None):
        """
        API endpoint allowing MEMBERSHIP programs to be
        viewed or edited.
        """
        return Response(MembershipProgramSerializer(
            FidelityProgram.objects.filter(program_type=FidelityProgram.MEMBERSHIP).order_by('name'),
            many=True,
            context={'request': request}).data)

    @action(detail=False)
    def cashbackprograms(self, request, pk=None):
        """
        API endpoint allowing CASHBACK programs to be
        viewed or edited.
        """
        return Response(CashbackProgramSerializer(
            FidelityProgram.objects.filter(program_type=FidelityProgram.CASHBACK).order_by('name'),
            many=True,
            context={'request': request}).data)

    @action(detail=True, methods=['post'])
    @pointsprograms.mapping.post
    def create_points_program(self, request, pk=None):
        """
        API endpoint allowing POINTS programs to be
        stored.
        """
        serializer = PointsProgramSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @levelsprograms.mapping.post
    def create_levels_program(self, request, pk=None):
        """
        API endpoint allowing LEVELS programs to be
        stored.
        """
        # fprogram = self.get_object()
        serializer = LevelsProgramSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @membershipprograms.mapping.post
    def create_membership_program(self, request, pk=None):
        """
        API endpoint allowing MEMBERSHIP programs to be
        stored.
        """
        # fprogram = self.get_object()
        serializer = MembershipProgramSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @cashbackprograms.mapping.post
    def create_cashback_program(self, request, pk=None):
        """
        API endpoint allowing CASHBACK programs to be
        stored.
        """
        # fprogram = self.get_object()
        serializer = CashbackProgramSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)



class CatalogueViewSet(viewsets.ModelViewSet):
    """
    API endpoint allowing Catalogue elements to be 
    viewed or edited.
    """
    queryset = Catalogue.objects.all()
    serializer_class = CatalogueSerializer

    @action(
        detail=False,
        methods=['get'],
        url_path=r'byuser/(?P<customer>\w+)'
    )
    def get_by_user(self, request, customer, pk=None):
        try:
            return Response(self.serializer_class(
                Catalogue.objects.filter(customer_id=customer),
                many=True,
                context={'request': request}).data)
        except Catalogue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    @action(
        detail=False,
        methods=['get'],
        url_path=r'byprogram/(?P<programname>(\w|\s)+)',
    )
    def get_by_fidelity_program(self, request, programname, pk=None):
        try:
            return Response(self.serializer_class(
                Catalogue.objects.filter(fidelity_program_id=programname),
                many=True,
                context={'request': request}).data)
        except Catalogue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    

    @action(
        detail=False,
        methods=['get'],
        url_path=r'(?P<customer>\w+)/(?P<programname>(\w|\s)+)',
    )
    def get_by_user_and_fidelity_program(self, request, customer, programname, pk=None):
        try:
            return Response(self.serializer_class(
                Catalogue.objects.filter(customer_id=customer).filter(fidelity_program_id=programname).get(),
                context={'request': request}).data)
        except Catalogue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)