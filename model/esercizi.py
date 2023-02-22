import json
from Bio.KEGG import REST
from flask import Blueprint, jsonify
import requests


class Api:
    def __init__(self):
        kegg = 'http://rest.kegg.jp/'
        self.list = kegg + 'list/'
        self.url_to_kegg = kegg + '/list/organism'
        self.get_genes_by_enzime = kegg + '/link/'
        self.look_4_dbname_idenifier = kegg + 'get/'

    @staticmethod
    def get_all_organism_dictionary():
        my_dict = []
        legg = REST.kegg_list('organism').read().split('\n')
        for g in legg:
            my_dict.append(g.split('\t'))
        return my_dict

    def api_to_k(self):
        api_to_k = Blueprint('es1_api', __name__)

        @api_to_k.route('/es1', methods=['GET'])
        def kegg():
            return Model().request_es1()

        @api_to_k.route('/es2/' + '<enzime>' + '/' + '<code>', methods=['GET'])
        def look_for(enzime, code):
            return Model().request_es2(enzime, code)

        @api_to_k.route('/es3/' + '<who>', methods=['GET'])
        def look_for_organism(who):
            return jsonify(Model().request_es3(who))

        @api_to_k.route('/es4/' + '<who>', methods=['GET'])
        def look_for_position(who):
            return Model().request_es4(who)

        @api_to_k.route('/es5_look_for/' + '<who>', methods=['GET'])
        def look_organism(who):
            return Model().request_es5(who)

        @api_to_k.route('/es5_get_all/' + '<code>', methods=['GET'])
        def get_all(code):
            return Model().request_es5_get_all(code)

        @api_to_k.route('/es5_enzima/' + '<enzima>')
        def get_enzima(enzima):
            return Model().request_es5_get_enzima(enzima)

        @api_to_k.route('/es6_get_all')
        def get_all_es6():
            return Model().request_es6_get_all_es6()

        @api_to_k.route('/es6/' + '<method>' + '/' + '<who>', methods=['GET'])
        def look_all_kegg(method, who):
            return Model().request_es6(method, who)
        return api_to_k


class Model(Api):
    def __init__(self):
        super(Model, self).__init__()

    def request_es1(self):
        all_kegg = requests.get(self.url_to_kegg)
        if all_kegg.status_code == 200:
            kegg_content = all_kegg.content
            print(kegg_content)
            return kegg_content

    def request_es2(self, enzima, org_code):
        i_will_look_for = str(self.get_genes_by_enzime + enzima + '/' + org_code)
        response = requests.get(i_will_look_for)
        return str(response.content.decode("utf-8"))

    def request_es3(self, who):
        my_dict = []
        i_will_look_for = str(self.look_4_dbname_idenifier + who)
        response = requests.get(i_will_look_for)
        response = (str(response.text).split('\n'))
        for element in response:
            my_dict.append(element)
        return my_dict

    def request_es4(self, who):
        i_will_get_the_position = str(self.look_4_dbname_idenifier + who)
        response = requests.get(i_will_get_the_position)
        response = response.content.decode('utf-8')
        position = response.find('POSITION')
        motif = response.find('MOTIF')
        value = response[position:motif]
        print(value)
        return value

    def request_es5(self, who):
        result = []
        result_ = []
        allcode = []
        organisms = self.get_all_organism_dictionary()
        for organism in organisms:
            try:
                enz = organism[1]
                # all_enz = self.get_all_enz_from_pathway(enz)
                # for e in all_enz:
                #     all_codes_for_specie = self.get_organism_source_code(e)
                specie = organism[2]
                domain = organism[3]
            except:
                continue
            if who in organism or self.match_it_with_specie_or_domain(who, specie, domain):
                result.append(organism)
        '''for element in result:
            enz = element[1]
            all_enz = self.get_all_enz_from_pathway(enz)
            result_.append(all_enz)
        result.append(result_)
        for e in result_:
            for k in e:
                all_codes_for_specie = self.get_organism_source_code(k)
                allcode.append(all_codes_for_specie)
        result.append(allcode)'''
        if result:
            return jsonify(result)
        else:
            return jsonify('No element has been found :/')

    def request_es5_get_all(self, code):
        request = requests.get(self.list + code)
        request_ = request.content.decode("utf-8")
        request_ = request_.split('\n')
        return jsonify(request_)

    def request_es5_get_enzima(self, enzima):
        request = requests.get(self.look_4_dbname_idenifier + enzima)
        request_ = request.content.decode("utf-8")
        request_ = request_.split('\n')
        return jsonify(request_)

    def request_es6_get_all_es6(self):
        organisms = self.get_all_organism_dictionary()
        array_organism = []
        for organism in organisms:
            array_organism.append(organism)
        return jsonify(array_organism)

    def request_es6(self, method, who):
        methods = ['info', 'list', 'find', 'get_all']
        if method in methods:
            if method == 'info':
                all = REST.kegg_info(who).read()
                print(all)
                return all
            elif method == 'list':
                all = REST.kegg_list(who).read()
                print(all)
                return all
            elif method == 'find':
                code = REST.kegg_get('eco:b0004', 'ntseq').read()
                print(code)
                return code
            elif method == 'get_all':
                organisms = self.get_all_organism_dictionary()
        else:
            return 'Incorrect method'

    @staticmethod
    def match_it_with_specie_or_domain(who, specie, domain):
        if who in specie or who in domain:
            return True
        else:
            return False

    @staticmethod
    def get_all_enz_from_pathway(enz):
        list_all = []
        link = 'http://rest.kegg.jp/link/pathway/'
        api = link + enz
        results = requests.get(api)
        if results.status_code == 200:
            result_ = results.content.decode('utf-8')
            result_ = result_.split('\n')
            for line in result_:
                line_ = line.split('\t', 1)
                list_all.append(line_[0])
            return list_all

    @staticmethod
    def get_organism_source_code(e):
        link = 'http://rest.kegg.jp/get/' + e + '/ntseq'
        response = requests.get(link)
        return response.content
