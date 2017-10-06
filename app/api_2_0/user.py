from flask.views import MethodView
from flask import g, request, make_response, jsonify, current_app, redirect, url_for, abort
from app.api_2_0.authentication import get_user_id, login_required
from ..models import User, BlacklistToken, Company
from .. import db
from . import api


class UserCompaniesAPI(MethodView):
    """
    Retrieve a user's favorite companies
    """
    decorators = [login_required]

    def get(self):
        # print "Your auth header", request.headers.get('Authorization')
        user_id = get_user_id()
        # print "Your user id", user_id
        user = User.query.filter_by(id=user_id).first()

        company_list = []
        for company in user.companies.all():
            company_list.append(company.to_json())

        response_object = {
            'status': 'success',
            'message': 'you have received this message',
            'companies': company_list
        }
        return make_response(jsonify(response_object)), 200


class UpdateLikeAPI(MethodView):
    """
    Like/dislike a company for a user
    """
    decorators = [login_required]

    def post(self):
        response_object = {
            'status': 'success',
            'message': 'you have liked the object',
        }
        json = request.get_json()
        user_id = get_user_id()
        like = json.get('like')
        symbol = json.get('symbol')

        if user_id and symbol:
            u = User.query.filter_by(id=user_id).first()
            c = Company.query.filter_by(symbol=symbol).first()
            if c:
                if like == "true":
                    if c not in u.companies.all():
                        u.companies.append(c)
                        db.session.commit()
                else:
                    if c in u.companies.all():
                        u.companies.remove(c)
                        db.session.commit()

                return make_response(jsonify(response_object)), 201

        response_object['status'] = "fail"
        response_object['message'] = "Could not locate object"
        return make_response(jsonify(response_object)), 400


class UserFavoriteWithCompanyAPI(MethodView):
    """
    Return a company object and the user's favorite status.
    """

    def get(self, symbol):
        user_id = get_user_id()
        user = User.query.filter_by(id=user_id).first()
        company = Company.query.filter_by(symbol=symbol).first()

        if not company:
            abort(404)

        if company in user.companies.all():
            favorite = True
        else:
            favorite = False

        d = company.to_json()
        d.update({"favorite": favorite})

        return jsonify(d)


user_companies_view = UserCompaniesAPI.as_view('user_companies_api')
user_like_view = UpdateLikeAPI.as_view('user_like_api')
user_favorite_with_company_view = UserFavoriteWithCompanyAPI.as_view('user_favorite_with_company_api')

api.add_url_rule('/user/companies', view_func=user_companies_view, methods=['GET'])
api.add_url_rule('/user/like', view_func=user_like_view, methods=['POST'])
api.add_url_rule('/user/company/<symbol>', view_func=user_favorite_with_company_view, methods=['GET'])

