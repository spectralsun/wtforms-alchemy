from pytest import raises
import sqlalchemy as sa
from wtforms.validators import (
    Email, InputRequired, DataRequired
)
from wtforms_alchemy import Unique, ModelForm
from tests import ModelFormTestCase


class TestAutoAssignedValidators(ModelFormTestCase):
    def test_auto_assigns_length_validators(self):
        self.init()
        self.assert_max_length('test_column', 255)

    def test_assigns_validators_from_info_field(self):
        self.init(info={'validators': Email()})
        self.assert_has_validator('test_column', Email)

    def test_assigns_unique_validator_for_unique_fields(self):
        self.init(unique=True)
        self.assert_has_validator('test_column', Unique)

    def test_raises_exception_if_no_session_set_for_unique_validators(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Unicode(255), unique=True)

        with raises(Exception):
            class ModelTestForm(ModelForm):
                class Meta:
                    model = ModelTest

    def test_assigns_non_nullable_fields_as_required(self):
        self.init(nullable=False)
        self.assert_has_validator('test_column', DataRequired)
        self.assert_has_validator('test_column', InputRequired)

    def test_string_not_nullable_validator_fallback(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Unicode(255), nullable=False)

        validator = DataRequired()

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_str_validator = None
                not_null_validator = validator

        form = ModelTestForm()
        assert validator in form.test_column.validators

    def test_configure_not_null_validator(self):
        class ModelTest(self.base):
            __tablename__ = 'model_test'
            id = sa.Column(sa.Integer, primary_key=True)
            test_column = sa.Column(sa.Boolean, nullable=False)

        class ModelTestForm(ModelForm):
            class Meta:
                model = ModelTest
                not_null_str_validator = None
                not_null_validator = None

        form = ModelTestForm()
        assert form.test_column.validators == []

    def test_not_nullable_booleans_are_required(self):
        self.init(sa.Boolean, nullable=False)
        self.assert_has_validator('test_column', InputRequired)

    def test_not_nullable_fields_with_defaults_are_not_required(self):
        self.init(nullable=False, default=u'default')
        self.assert_not_required('test_column')

    def test_assigns_not_nullable_integers_as_optional(self):
        self.init(sa.Integer, nullable=True)
        self.assert_optional('test_column')
