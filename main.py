from website import create_app
#flask uygulamasının yalnızca oluşumunu sağlayan fonksiyon
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)