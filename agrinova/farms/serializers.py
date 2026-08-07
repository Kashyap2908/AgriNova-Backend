from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FarmerProfile, Farm
from .services import fetch_coordinates_nominatim

class FarmerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for FarmerProfile.
    Accepts both standard snake_case and frontend camelCase field aliases.
    Automatically flags profile_completed = True upon valid save.
    """
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    user_id = serializers.ReadOnlyField(source='user.id')

    fullName = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = FarmerProfile
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'full_name',
            'phone_number',
            'preferred_language',
            'profile_photo',
            'profile_completed',
            'created_at',
            'updated_at',
            # Field Aliases
            'fullName',
            'phone',
            'language'
        ]
        read_only_fields = ['id', 'user_id', 'username', 'email', 'profile_completed', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # Map frontend camelCase fields to backend model fields
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        if 'fullName' in mutable_data and not mutable_data.get('full_name'):
            mutable_data['full_name'] = mutable_data['fullName']
        if 'phone' in mutable_data and not mutable_data.get('phone_number'):
            mutable_data['phone_number'] = mutable_data['phone']
        if 'language' in mutable_data and not mutable_data.get('preferred_language'):
            mutable_data['preferred_language'] = mutable_data['language']
            
        return super().to_internal_value(mutable_data)

    def validate(self, attrs):
        full_name = attrs.get('full_name')
        phone_number = attrs.get('phone_number')

        if not full_name and not self.instance:
            raise serializers.ValidationError({"full_name": "Full name is required."})
        if not phone_number and not self.instance:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('fullName', None)
        validated_data.pop('phone', None)
        validated_data.pop('language', None)
        
        validated_data['profile_completed'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('fullName', None)
        validated_data.pop('phone', None)
        validated_data.pop('language', None)
        
        validated_data['profile_completed'] = True
        return super().update(instance, validated_data)


class FarmSerializer(serializers.ModelSerializer):
    """
    Serializer for Farm model with validation, frontend alias mapping,
    and automatic geocoding.
    """
    name = serializers.CharField(write_only=True, required=False)
    area = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    areaUnit = serializers.CharField(write_only=True, required=False)
    pinCode = serializers.CharField(write_only=True, required=False)
    soil = serializers.CharField(write_only=True, required=False)
    soilType = serializers.CharField(write_only=True, required=False)
    irrigation = serializers.CharField(write_only=True, required=False)
    irrigationType = serializers.CharField(write_only=True, required=False)
    waterAvailability = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Farm
        fields = [
            'id',
            'user',
            'farm_name',
            'state',
            'district',
            'taluka',
            'village',
            'pincode',
            'latitude',
            'longitude',
            'farm_area',
            'area_unit',
            'soil_type',
            'irrigation_type',
            'water_availability',
            'is_active',
            'nitrogen',
            'phosphorus',
            'potassium',
            'soil_ph',
            'sulphur',
            'calcium',
            'magnesium',
            'zinc',
            'boron',
            'iron',
            'manganese',
            'copper',
            'organic_carbon',
            'electrical_conductivity',
            'soil_moisture',
            'last_soil_test_date',
            'created_at',
            'updated_at',
            # Field Aliases
            'name',
            'area',
            'areaUnit',
            'pinCode',
            'soil',
            'soilType',
            'irrigation',
            'irrigationType',
            'waterAvailability'
        ]
        read_only_fields = ['id', 'user', 'latitude', 'longitude', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)

        # Alias mappings
        if 'name' in mutable_data and not mutable_data.get('farm_name'):
            mutable_data['farm_name'] = mutable_data['name']
        if 'area' in mutable_data and not mutable_data.get('farm_area'):
            mutable_data['farm_area'] = mutable_data['area']
        if 'areaUnit' in mutable_data and not mutable_data.get('area_unit'):
            mutable_data['area_unit'] = mutable_data['areaUnit']
        if 'pinCode' in mutable_data and not mutable_data.get('pincode'):
            mutable_data['pincode'] = mutable_data['pinCode']
        if 'soilType' in mutable_data and not mutable_data.get('soil_type'):
            mutable_data['soil_type'] = mutable_data['soilType']
        elif 'soil' in mutable_data and not mutable_data.get('soil_type'):
            mutable_data['soil_type'] = mutable_data['soil']
        if 'irrigationType' in mutable_data and not mutable_data.get('irrigation_type'):
            mutable_data['irrigation_type'] = mutable_data['irrigationType']
        elif 'irrigation' in mutable_data and not mutable_data.get('irrigation_type'):
            mutable_data['irrigation_type'] = mutable_data['irrigation']
        if 'waterAvailability' in mutable_data and not mutable_data.get('water_availability'):
            mutable_data['water_availability'] = mutable_data['waterAvailability']
        if 'organicCarbon' in mutable_data and not mutable_data.get('organic_carbon'):
            mutable_data['organic_carbon'] = mutable_data['organicCarbon']
        if 'electricalConductivity' in mutable_data and not mutable_data.get('electrical_conductivity'):
            mutable_data['electrical_conductivity'] = mutable_data['electricalConductivity']
        if 'soilMoisture' in mutable_data and not mutable_data.get('soil_moisture'):
            mutable_data['soil_moisture'] = mutable_data['soilMoisture']
        if 'soilPh' in mutable_data and not mutable_data.get('soil_ph'):
            mutable_data['soil_ph'] = mutable_data['soilPh']

        # Clean empty string "" -> None for numeric & optional fields
        nullable_numeric_fields = [
            'nitrogen', 'phosphorus', 'potassium', 'soil_ph',
            'sulphur', 'calcium', 'magnesium', 'zinc', 'boron',
            'iron', 'manganese', 'copper', 'organic_carbon',
            'electrical_conductivity', 'soil_moisture'
        ]
        for field in nullable_numeric_fields:
            if field in mutable_data and (mutable_data[field] == '' or mutable_data[field] is None):
                mutable_data[field] = None

        if 'last_soil_test_date' in mutable_data and not mutable_data['last_soil_test_date']:
            mutable_data['last_soil_test_date'] = None

        # Fallback values from existing instance for required text fields if partial update missing them
        if self.instance:
            if 'taluka' not in mutable_data or not mutable_data['taluka']:
                mutable_data['taluka'] = self.instance.taluka or self.instance.district or 'Central'
            if 'irrigation_type' not in mutable_data or not mutable_data['irrigation_type']:
                mutable_data['irrigation_type'] = self.instance.irrigation_type or 'Drip'
            if 'water_availability' not in mutable_data or not mutable_data['water_availability']:
                mutable_data['water_availability'] = self.instance.water_availability or 'Good'

        return super().to_internal_value(mutable_data)

    def validate_farm_area(self, value):
        if value <= 0:
            raise serializers.ValidationError("Farm area must be greater than zero.")
        return value

    def validate(self, attrs):
        farm_name = attrs.get('farm_name') or (self.instance and self.instance.farm_name)
        state = attrs.get('state') or (self.instance and self.instance.state)
        district = attrs.get('district') or (self.instance and self.instance.district)
        village = attrs.get('village') or (self.instance and self.instance.village)

        if not farm_name:
            raise serializers.ValidationError({"farm_name": "Farm name is required."})
        if not state:
            raise serializers.ValidationError({"state": "State is required."})
        if not district:
            raise serializers.ValidationError({"district": "District is required."})
        if not village:
            raise serializers.ValidationError({"village": "Village is required."})

        return attrs

    def clean_alias_fields(self, validated_data):
        aliases = ['name', 'area', 'areaUnit', 'pinCode', 'soil', 'soilType', 'irrigation', 'irrigationType', 'waterAvailability']
        for alias in aliases:
            validated_data.pop(alias, None)

    def create(self, validated_data):
        self.clean_alias_fields(validated_data)
        
        village = validated_data.get('village', '')
        taluka = validated_data.get('taluka', '')
        district = validated_data.get('district', '')
        state = validated_data.get('state', '')

        lat, lon = fetch_coordinates_nominatim(village, taluka, district, state)
        validated_data['latitude'] = lat
        validated_data['longitude'] = lon

        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.clean_alias_fields(validated_data)

        village = validated_data.get('village', instance.village)
        taluka = validated_data.get('taluka', instance.taluka)
        district = validated_data.get('district', instance.district)
        state = validated_data.get('state', instance.state)

        if (village != instance.village or district != instance.district or state != instance.state):
            lat, lon = fetch_coordinates_nominatim(village, taluka, district, state)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lon

        return super().update(instance, validated_data)


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class DashboardSerializer(serializers.Serializer):
    user = UserBasicSerializer()
    profile = FarmerProfileSerializer(allow_null=True)
    selected_farm = FarmSerializer(allow_null=True)
    total_farms = serializers.IntegerField()
    profile_completed = serializers.BooleanField()
