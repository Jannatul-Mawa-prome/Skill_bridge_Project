from pydantic import BaseModel, EmailStr, Field, model_validator


class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    roll: str = Field(..., min_length=1, max_length=30)
    semester: str
    edu_email: EmailStr
    mobile: str = Field(..., min_length=11, max_length=20)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and Confirm Password do not match.")
        return self


class UserLoginRequest(BaseModel):
    login_id: str = Field(..., description="Edu email or roll number")
    password: str = Field(..., min_length=8)