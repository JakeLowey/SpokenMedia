__author__ = 'Jake Lowey'
import os
import pymysql
import guessit
import tmdbsimple as tmdb

vlc_formats = (
    ".asx", ".dts", ".gxf", ".m2v", ".m3u", ".m4v", ".mpeg1", ".mpeg2", ".mts", ".mxf", ".omg", ".pls", ".bup", ".a52",
    ".aac", ".b4s", ".cue", ".divx", ".dv", ".flv", ".m1v", ".m2ts", ".mkv", ".mov", ".mpeg4", ".oma", ".spx", ".ts",
    ".vlc", ".vob", ".xspf", ".dat", ".bin", ".ifo", ".part", ".3g2", ".avi", ".mpeg", ".mpg", ".flac", ".m4a", ".mp1",
    ".ogg", ".wav", ".xm", ".3gp", ".srt", ".wmv", ".ac3", ".asf", ".mod", ".mp2", ".mp3", ".mp4", ".wma", ".mka",
    ".m4p")


def findclosest(title, year, response):
    if len(response) == 1:
        return response[0]['id']
    else:
        i = 0
        possibilities = []
        for movie in response:
            if movie['title'].lower() == title.lower() and movie['release_date'][0:4] == year:
                return movie['id']
            elif movie['title'] == title:
                possibilities.append(i)
            i += 1
        if len(possibilities) == 1:
            return response[possibilities[0]]['id']
        else:
            return -1


def createinsertstatement(location, info, db):
    ins = "INSERT INTO " + db + " (title, location"
    vals = " VALUES (`" + info.title + "`,`" + str(location) + "`"
    if info['genres']:
        ins += ", genres"
        vals += "`" + info['genres'] + "`"
    if info['playcount']:
        ins += ", playcount"
        vals += "`" + info['playcount'] + "`"
    if info['actors'] and db != "music":
        ins += ", actors"
        vals += "`" + info['actors'] + "`"
    if info['popularity']:
        ins += ", popularity"
        vals += "`" + info['popularity'] + "`"
    if info['releasedate']:
        ins += ", releasedate"
        vals += "`" + info['releasedate'] + "`"
    if info['director'] and db != "music":
        ins += ", director"
        vals += "`" + info['director'] + "`"
    if info['length']:
        ins += ", length"
        vals += "`" + info['length'] + "`"
    if info['description'] and db != "music":
        ins += ", description"
        vals += "`" + info['description'] + "`"
    if info['artist'] and db == "music":
        ins += ", artist"
        vals += "`" + info['artist'] + "`"
    if info['featuredartist'] and db == "music":
        ins += ", featuredartist"
        vals += "`" + info['featuredartist'] + "`"
    if info['album'] and db == "music":
        ins += ", album"
        vals += "`" + info['album'] + "`"
    if info['season'] and db == "tvshows":
        ins += ", season"
        vals += "`" + info['season'] + "`"
    if info['episode'] and db == "tvshows":
        ins += ", episode"
        vals += "`" + info['episode'] + "`"
    ins += " )"
    vals += " )"
    return ins + vals


class DataBase:
    def __init__(self):
        f = open("databaseconnection.txt")
        username = f.readline()
        username = username.strip('\n').strip('\r')
        password = f.readline()
        password = password.strip('\n').strip('\r')
        f.close()
        conn = pymysql.connect(host='localhost', port=3306, user=username, passwd=password, db='media')
        self.cur = conn.cursor()
        f = open("tmdbAPI.txt")
        tmdb.API_KEY = f.readline().strip('\n').strip('\r')
        f.close()
        self.search = tmdb.Search()

    def insertMovie(self, movieID,loc,fileName):
        if not self.isitthere("movies", loc):
            if int(movieID) > 0:
                identity = tmdb.Movies(int(movieID))
                movieInfo = identity.info()
                # Create insert statement
                insertStatement =  createinsertstatement(loc, movieInfo, "movies")
                # insert all the info into the database
                self.cur.execute(insertStatement)
            else:
                movieInfo = {"title": fileName}
                # Create insert statement
                insertStatement =  createinsertstatement(loc, movieInfo, "movies")
                # insert as much info as is known into the database
                self.cur.execute(insertStatement)
                return False
        return True



    def addmovies(self, path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(vlc_formats):
                    print(f)
                    guess = guessit.guess_movie_info(f, info=["filename"])
                    print(guess.nice_string())
                    try:
                        response = self.search.movie(query=(guess['title']))
                        movieID = findclosest(guess['title'], guess['year'], response)
                        tryInsert = self.insertMovie(movieID,os.join(root,f),f)
                        if not tryInsert:
                            pass

                    except:
                        pass

    def addtvshows(self, path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(vlc_formats):
                    print(f)
                    guess = guessit.guess_episode_info()

    def isitthere(db,loc):
        result = self.cur.execute("SELECT COUNT(*) FROM " + db + " where location = " + loc)
        if result == 0:
            return False
        else:
            return True