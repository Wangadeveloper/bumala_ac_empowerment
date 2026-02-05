from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from loan import db, bcrypt
from loan.forms import (
    RegistrationForm, LoginForm,
    UserProfileForm, ContributionForm,
    LoanApplicationForm
)
from loan.models import User, UserProfile, Contribution, Loan
from datetime import datetime

main = Blueprint('main', __name__)

# ---------------- HOME ----------------
@main.route('/')
@main.route('/home')
def home():
    return render_template('index.html')


# ---------------- AUTH ----------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_account'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_account'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.user_account'))
        flash("Invalid login details", "danger")
    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# ---------------- DASHBOARD ----------------
@main.route('/user_account')
@login_required
def user_account():
    approved_contributions = Contribution.query.filter_by(
        user_id=current_user.id,
        status="Approved"
    ).all()

    total_contributions = sum(c.amount for c in approved_contributions)

    active_loan = Loan.query.filter_by(
        user_id=current_user.id,
        status="Approved"
    ).first()

    return render_template(
        'account_info.html',
        total_contributions=total_contributions,
        active_loan=active_loan
    )


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm(obj=current_user.profile)

    if form.validate_on_submit():
        if current_user.profile:
            profile = current_user.profile
        else:
            profile = UserProfile(user_id=current_user.id)

        # Personal Info
        profile.full_names = form.full_names.data
        profile.phone_no = form.phone.data
        profile.country = form.country.data
        profile.location = form.location.data
        profile.email = form.email.data

        # Financial Info
        profile.savings_category = form.savings_category.data
        profile.payment_level = form.payment_level.data
        profile.goals = form.goals.data

        # Mark profile as completed
        current_user.profile_completed = True

        db.session.add(profile)
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('main.user_account'))

    # Pre-fill existing data for GET
    if current_user.profile:
        form.savings_category.data = current_user.profile.savings_category
        form.payment_level.data = current_user.profile.payment_level
        form.goals.data = current_user.profile.goals

    return render_template('profile.html', form=form)



# ---------------- CONTRIBUTIONS ----------------
@main.route('/submit-contribution', methods=['GET', 'POST'])
@login_required
def submit_contribution():
    form = ContributionForm()
    if form.validate_on_submit():
        contribution = Contribution(
            user_id=current_user.id,
            amount=form.amount.data,
            transaction_code=form.transaction_code.data,
            status="Pending",  # default status
            created_at=datetime.utcnow()
        )
        db.session.add(contribution)
        db.session.commit()
        flash("Contribution submitted successfully and is pending approval.", "success")
        
        # Redirect to updated contribution history
        return redirect(url_for('main.contribution_history'))

    return render_template('submit_contribution.html', form=form)


@main.route('/contribution-history')
@login_required
def contribution_history():
    contributions = Contribution.query.filter_by(
        user_id=current_user.id
    ).order_by(Contribution.created_at.desc()).all()

    return render_template(
        'contribution_history.html',
        contributions=contributions
    )



# ---------------- MEMBERSHIP LOANS ----------------
@main.route('/membership-loans', methods=['GET', 'POST'])
@login_required
def membership_loans():
    form = LoanApplicationForm()

    # Fetch approved contributions
    approved_contributions = Contribution.query.filter_by(
        user_id=current_user.id,
        status="Approved"
    ).all()
    total_contributions = sum(c.amount for c in approved_contributions)
    max_loan = total_contributions * 3  # Example SACCO rule

    # Fetch existing active loan
    existing_loan = Loan.query.filter_by(
        user_id=current_user.id,
        status="Approved"
    ).first()

    # Fetch user profile info
    profile = current_user.profile
    if profile:
        savings_category = profile.savings_category or "Not set"
        payment_level = profile.payment_level or "Not set"
    else:
        savings_category = "Not set"
        payment_level = "Not set"

    # Map payment level to actual KES value
    payment_mapping = {
        '1': 'Level 1 - KSh 100',
        '2': 'Level 2 - KSh 200',
        '3': 'Level 3 - KSh 300',
        '4': 'Level 4 - KSh 400',
        '5': 'Level 5 - KSh 500'
    }
    payment_display = payment_mapping.get(payment_level, "Not set")

    # Map savings category to display text
    savings_display = "Weekly Contribution" if savings_category == "weekly" else (
        "Monthly Contribution" if savings_category == "monthly" else "Not set"
    )

    # Handle form submission
    if form.validate_on_submit():
        if existing_loan:
            flash("You already have an active loan", "warning")
            return redirect(url_for('main.loan_status'))

        if form.amount.data > max_loan:
            flash("Requested amount exceeds your loan eligibility", "danger")
            return redirect(url_for('main.membership_loans'))

        loan = Loan(
            user_id=current_user.id,
            amount=form.amount.data,
            purpose=form.purpose.data,
            repaid_amount=0,
            status="Pending",
            created_at=datetime.utcnow()
        )
        db.session.add(loan)
        db.session.commit()
        flash("Loan application submitted for approval", "success")
        return redirect(url_for('main.user_account'))

    return render_template(
        'membership_loans.html',
        form=form,
        total_contributions=total_contributions,
        max_loan=max_loan,
        savings_display=savings_display,
        payment_display=payment_display
    )


# ---------------- LOAN STATUS & REPAYMENTS ----------------
@main.route('/loan-status')
@login_required
def loan_status():
    loan = Loan.query.filter_by(
        user_id=current_user.id
    ).order_by(Loan.created_at.desc()).first()

    if not loan:
        flash("You have no loan records", "info")
        return redirect(url_for('main.membership_loans'))

    repaid = loan.repaid_amount or 0
    remaining = loan.amount - repaid
    progress = int((repaid / loan.amount) * 100) if loan.amount else 0

    return render_template(
        'loan_status.html',
        loan=loan,
        repaid_amount=repaid,
        remaining_balance=remaining,
        progress_percent=progress
    )
