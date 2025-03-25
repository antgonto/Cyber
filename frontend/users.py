# backend/app/dash_app.py
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import requests
import json
from django.urls import reverse

# Initialize Dash app
dash_app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    url_base_pathname='/dashboard/'
)

# Define the layout
dash_app.layout = html.Div([
    dbc.Container([
        html.H1("User Management Dashboard", className="my-4"),

        # Tabs for different operations
        dbc.Tabs([
            # View Users Tab
            dbc.Tab(label="View Users", children=[
                html.Div([
                    dbc.Button("Refresh", id="refresh-users", color="primary", className="mt-3 mb-3"),
                    dash_table.DataTable(
                        id='users-table',
                        columns=[
                            {'name': 'ID', 'id': 'user_id'},
                            {'name': 'Username', 'id': 'username'},
                            {'name': 'Email', 'id': 'email'},
                            {'name': 'Role', 'id': 'role'},
                            {'name': 'Last Login', 'id': 'last_login'}
                        ],
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                    )
                ])
            ], tab_id="view-users"),

            # Create User Tab
            dbc.Tab(label="Create User", children=[
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Username"),
                            dbc.Input(id="new-username", type="text", placeholder="Enter username"),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Email"),
                            dbc.Input(id="new-email", type="email", placeholder="Enter email"),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Password"),
                            dbc.Input(id="new-password", type="password", placeholder="Enter password"),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Role"),
                            dcc.Dropdown(
                                id="new-role",
                                options=[
                                    {'label': 'Administrator', 'value': 'admin'},
                                    {'label': 'Security Analyst', 'value': 'analyst'},
                                    {'label': 'Security Manager', 'value': 'manager'},
                                    {'label': 'Regular User', 'value': 'user'},
                                ],
                                value="user",
                            ),
                        ]),
                    ], className="mb-3"),
                    dbc.Button("Create User", id="create-user-button", color="success", className="mt-3"),
                    html.Div(id="create-user-result", className="mt-3")
                ])
            ], tab_id="create-user"),

            # Edit User Tab
            dbc.Tab(label="Edit User", children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Select User"),
                        dcc.Dropdown(id="edit-user-select"),
                    ]),
                ], className="mb-3"),
                html.Div(id="edit-user-form"),
                html.Div(id="edit-user-result", className="mt-3")
            ], tab_id="edit-user"),

            # Delete User Tab
            dbc.Tab(label="Delete User", children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Select User"),
                        dcc.Dropdown(id="delete-user-select"),
                    ]),
                ], className="mb-3"),
                dbc.Button("Delete User", id="delete-user-button", color="danger", className="mt-3"),
                html.Div(id="delete-user-result", className="mt-3")
            ], tab_id="delete-user")
        ], id="tabs", active_tab="view-users"),
    ], fluid=True)
])


# Callbacks
@dash_app.callback(
    Output('users-table', 'data'),
    Input('refresh-users', 'n_clicks')
)
def refresh_users_table(n_clicks):
    try:
        response = requests.get("/api/users/")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


@dash_app.callback(
    [Output('edit-user-select', 'options'),
     Output('delete-user-select', 'options')],
    Input('refresh-users', 'n_clicks')
)
def update_user_dropdowns(n_clicks):
    try:
        response = requests.get("/api/users/")
        if response.status_code == 200:
            users = response.json()
            options = [{'label': f"{user['username']} ({user['email']})", 'value': user['user_id']} for user in users]
            return options, options
        return [], []
    except Exception as e:
        print(f"Error fetching users for dropdowns: {e}")
        return [], []


@dash_app.callback(
    Output('create-user-result', 'children'),
    Input('create-user-button', 'n_clicks'),
    [State('new-username', 'value'),
     State('new-email', 'value'),
     State('new-password', 'value'),
     State('new-role', 'value')]
)
def create_user(n_clicks, username, email, password, role):
    if not n_clicks:
        return ""

    if not username or not email or not password:
        return html.Div("All fields are required!", className="text-danger")

    try:
        data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        response = requests.post("/api/users/", json=data)

        if response.status_code == 200:
            return html.Div("User created successfully!", className="text-success")
        else:
            return html.Div(f"Error: {response.text}", className="text-danger")
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="text-danger")


@dash_app.callback(
    Output('edit-user-form', 'children'),
    Input('edit-user-select', 'value')
)
def populate_edit_form(user_id):
    if not user_id:
        return ""

    try:
        response = requests.get(f"/api/users/{user_id}")
        if response.status_code == 200:
            user = response.json()
            return html.Div([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Username"),
                            dbc.Input(id="edit-username", type="text", value=user['username']),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Email"),
                            dbc.Input(id="edit-email", type="email", value=user['email']),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Password"),
                            dbc.Input(id="edit-password", type="password",
                                      placeholder="Leave blank to keep current password"),
                        ]),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Role"),
                            dcc.Dropdown(
                                id="edit-role",
                                options=[
                                    {'label': 'Administrator', 'value': 'admin'},
                                    {'label': 'Security Analyst', 'value': 'analyst'},
                                    {'label': 'Security Manager', 'value': 'manager'},
                                    {'label': 'Regular User', 'value': 'user'},
                                ],
                                value=user['role'],
                            ),
                        ]),
                    ], className="mb-3"),
                    dbc.Button("Update User", id="update-user-button", color="primary", className="mt-3"),
                ])
            ])
        return html.Div("User not found", className="text-danger")
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="text-danger")


@dash_app.callback(
    Output('edit-user-result', 'children'),
    Input('update-user-button', 'n_clicks'),
    [State('edit-user-select', 'value'),
     State('edit-username', 'value'),
     State('edit-email', 'value'),
     State('edit-password', 'value'),
     State('edit-role', 'value')]
)
def update_user(n_clicks, user_id, username, email, password, role):
    if not n_clicks or not user_id:
        return ""

    try:
        data = {}
        if username:
            data['username'] = username
        if email:
            data['email'] = email
        if password:
            data['password'] = password
        if role:
            data['role'] = role

        response = requests.put(f"/api/users/{user_id}", json=data)

        if response.status_code == 200:
            return html.Div("User updated successfully!", className="text-success")
        else:
            return html.Div(f"Error: {response.text}", className="text-danger")
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="text-danger")


@dash_app.callback(
    Output('delete-user-result', 'children'),
    Input('delete-user-button', 'n_clicks'),
    State('delete-user-select', 'value')
)
def delete_user(n_clicks, user_id):
    if not n_clicks or not user_id:
        return ""

    try:
        response = requests.delete(f"/api/users/{user_id}")

        if response.status_code == 200:
            return html.Div("User deleted successfully!", className="text-success")
        else:
            return html.Div(f"Error: {response.text}", className="text-danger")
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="text-danger")