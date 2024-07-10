from .app import create_app
from flask import Flask, request, url_for, redirect, render_template

app = create_app()

if  __name__ == '__main__':
    app.run(debug=True)