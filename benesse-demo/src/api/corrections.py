from flask import request, jsonify, abort
from werkzeug.exceptions import BadRequest, InternalServerError

from . import api
from .model.interactive_copy import getModel, runInference
from .model.hunspell_custom import getSpellChecker
from .model.fmtout import grammar_correction_json
import re

reqs = getModel()
spellchecker = getSpellChecker()
print('models_loaded')


@api.route("/corrections", methods=["POST"])
def dashboard():
    text = request.form.get('text')
    if text is None or text == '':
        raise BadRequest('Request param text is missing')
    sentence = re.sub('\\n|<\s?\w+>?\s?|<unw>|<unc>|<|>|\\r|\r', '', text)
    try:
        correction = runInference(reqs, spellchecker, sentences=[[sentence]])
        result = grammar_correction_json(sentence, correction)
    except Exception as e:
        raise InternalServerError(e)

    return jsonify(result)
