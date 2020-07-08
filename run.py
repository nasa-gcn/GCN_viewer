from flask_backend import create_app
app = create_app()

if __name__ == '__main__':
	app.run(host='localhost', debug=True, port=5000)\

