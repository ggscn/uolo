from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for

from flask_app.blueprints.analysis.forms import SearchForm
from flask_app.blueprints.user.models import User
from flask_app.blueprints.watchlist.models import WatchlistItem, Watchlist
from flask_app.blueprints.watchlist.forms import SearchForm, WatchlistBulkDeleteForm, WatchlistForm
from flask_app.blueprints.analysis.models import StockPrice
from flask_app.extensions import limiter
from lib.company import Tiingo
from sqlalchemy import text

watchlist = Blueprint('watchlist', __name__, template_folder='templates')

@watchlist.route('/watchlists/', defaults={'page': 1})
@watchlist.route('/watchlists/page/<int:page>')
def categories(page):
    search_form = SearchForm()
    bulk_form = WatchlistBulkDeleteForm()

    sort_by = Watchlist.sort_by(request.args.get('sort', 'name'),
                           request.args.get('direction', 'desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_categories = Watchlist.query.filter(
        Watchlist.name.ilike(request.args.get('query', ''))
    ).order_by(
        Watchlist.name.asc(), text(order_values)
    ).paginate(page=page, per_page=50)

    return render_template('watchlist/index.html',
                           form=search_form, bulk_form=bulk_form,
                           categories=paginated_categories)

@watchlist.route('/watchlists/new')
def watchlist_new():
    coupon = Watchlist()
    form = WatchlistForm(obj=coupon)

    if form.validate_on_submit():
        form.populate_obj(coupon)

        return redirect(url_for('admin.coupons'))

    return render_template('admin/coupon/new.html', form=form, coupon=coupon)

@watchlist.route('/list/categories/bulk_delete', methods=['POST'])
def categories_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = WatchListCategory.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       omit_ids=[current_user.id],
                                       query=request.args.get('query', ''))

        # Prevent circular imports.
        from snakeeyes.blueprints.billing.tasks import delete_users

        delete_users.delay(ids)

        flash('{0} user(s) were scheduled to be deleted.'.format(len(ids)),
              'success')
    else:
        flash('No users were deleted, something went wrong.', 'error')

    return redirect(url_for('admin.users'))