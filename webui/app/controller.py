import requests
from app import classifier
from flask import Blueprint, request, send_from_directory, jsonify
from flask_cors import CORS

# Define Blueprint(s)
mod_app = Blueprint('application', __name__, url_prefix='/explorer-api')
CORS(mod_app)

# Define Controller(s)
@mod_app.route('/')
def index():
    return send_from_directory('static/pages', 'index.html')

@mod_app.route('/classify/createnew/<model>', methods=['GET'])
def create_new_model(model):
    ## TODO need to deal with naming models
    print("here")
    #classifier.clear_model()
    classifier.new_model(model)
    return("done")


@mod_app.route('/classify/listmodels', methods=['GET'])
def list_models():
    return jsonify(classifier.get_models())


# POST Requests
@mod_app.route('/classify/update/<model>', methods=['POST'])
def build_model(model):
    ## TODO Specify model
    annotations = []
    data = request.get_json()
    for key, value in data.iteritems():
        annotations.append(int(value))
    #for item in data.split('&'):
    #    annotations.append(int(item.split('=')[1]))

    accuracy = classifier.update_model(model, annotations)
    return accuracy


@mod_app.route('/classify/upload/<model>', methods=['POST'])
def upload_model(model):
    ## TODO Specify model
    return classifier.import_model(model)


@mod_app.route('/classify/download/<model>', methods=['POST'])
def download_model(model):
    ## TODO Specify model
    return classifier.export_model(model)


@mod_app.route('/classify/exist/<model>', methods=['POST'])
def check_model(model):
    return classifier.check_model(model)

@mod_app.route('/classify/stats/<model>', methods=['GET'])
def model_stats(model):
    return classifier.check_model(model)

@mod_app.route('/cmd/crawler/exist/<model>', methods=['POST'])
def check_crawl_exists(model):
    ## TODO Specify model
    ## TODO FIX URL for scale out
    return requests.post("http://sparkler:6000/cmd/crawler/exist/").text


@mod_app.route('/cmd/crawler/crawl/<model>', methods=['POST'])
def start_crawl(model):
    f=open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r")
    token =""
    if f.mode == 'r':
        token =f.read()
    cmd = ["/data/sparkler/bin/sparkler.sh", "crawl", "-cdb", "http://sce-solr:8983/solr/crawldb", "-id", model]
    json = {"kind": "Pod", "apiVersion": "v1",
            "metadata": {"name": model+"crawl", "labels": {"run": model+"seed"}}, "spec": {
            "containers": [
                {"name": model+"crawl", "image": "registry.gitlab.com/sparkler-crawl-environment/sparkler/sparkler:memex-dd", "command": cmd,
                 "resources": {}}], "restartPolicy": "Never", "dnsPolicy": "ClusterFirst"}, "status": {}}
    requests.post('https://kubernetes.default.svc.cluster.local/api/v1/namespaces/default/pods', json=json, headers={"content-type":"application/json", "Authorization": "Bearer "+token}, verify=False)
    return "crawl started"

@mod_app.route('/cmd/crawler/crawler/<model>', methods=['GET'])
def crawl_status(model):
    f = open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r")
    token = ""
    if f.mode == 'r':
        token = f.read()
    r = requests.get('https://kubernetes.default.svc.cluster.local/api/v1/namespaces/default/pods'+model+'/status', headers={"content-type":"application/json", "Authorization": "Bearer "+token}, verify=False)
    return r.json()

@mod_app.route('/cmd/crawler/int/<model>', methods=['POST'])
def kill_crawl_gracefully(model):
    requests.delete("https://kubernetes.default.svc.cluster.local/api/v1/namespaces/default/pods/"+model+"crawl")
    return "crawl killed"


@mod_app.route('/cmd/crawler/kill/<model>', methods=['POST'])
def force_kill_crawl(model):
    requests.delete("https://kubernetes.default.svc.cluster.local/api/v1/namespaces/default/pods/"+model+"crawl")
    return "crawl killed"


@mod_app.route('/cmd/seed/upload/<model>', methods=['POST'])
def upload_seed(model):
    print request.get_data()
    ## TODO Come up with a way of updating the uploaded data.
    classifier.save_seeds(model, request.get_data())
    seeds =  request.get_data().splitlines()
    urls = ",".join(seeds)

    f=open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r")
    token =""
    if f.mode == 'r':
        token =f.read()
    cmd = ["/data/sparkler/bin/sparkler.sh", "inject", "-cdb", "http://sce-solr:8983/solr/crawldb", "-su", urls, "-id", model]
    json = {"kind": "Pod", "apiVersion": "v1",
             "metadata": {"name": model+"seed", "labels": {"run": model+"seed"}}, "spec": {
            "containers": [
                {"name": model+"seed", "image": "registry.gitlab.com/sparkler-crawl-environment/sparkler/sparkler:memex-dd", "command": cmd,
                 "resources": {}}], "restartPolicy": "Never", "dnsPolicy": "ClusterFirst"}, "status": {}}
    requests.post('https://kubernetes.default.svc.cluster.local/api/v1/namespaces/default/pods', json=json, headers={"content-type":"application/json", "Authorization": "Bearer "+token}, verify=False)
    return "seed urls uploaded"


