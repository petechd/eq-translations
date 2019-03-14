import unittest

from babel.messages import Catalog

from app.schema_translation import SchemaTranslation
from app.survey_schema import SurveySchema


class TestSurveySchema(unittest.TestCase):
    def test_get_messages(self):
        schema = SurveySchema()
        schema.load('./tests/schemas/test_translation.json')

        assert schema.pointers is not None

    def test_get_titles_messages(self):
        schema = SurveySchema({
            "type": "CalculatedSummary",
            "id": "block-3",
            "titles": [{
                "value": "Calculated Summary Main Title Block 2"
            }],
            "calculation": {
                "calculation_type": "sum",
                "answers_to_calculate": [
                    "first-number-answer",
                    "second-number-answer"
                ],
                "titles": [{
                    "value": "Calculated Summary Calculation Title Block 2"
                }]
            }
        })

        pointers = schema.get_titles_pointers()

        assert '/titles/0/value' in pointers
        assert '/calculation/titles/0/value' in pointers

        assert len(pointers) == 2

    def test_get_list_messages(self):
        schema = SurveySchema({
            "content": [{
                    "title": "Include:",
                    "list": [
                        "all employees in Great Britain (England, Scotland and Wales), both full and part-time, who received pay in the relevant period"
                    ]
                },
                {
                    "title": "Exclude:",
                    "list": [
                        "trainees on government schemes",
                        "employees working abroad unless paid directly from this business’s GB payroll",
                        "employees in Northern Ireland"
                    ]
                }
            ]
        })

        pointers = schema.get_list_pointers()

        assert "/content/0/list/0" in pointers
        assert "/content/1/list/0" in pointers
        assert "/content/1/list/1" in pointers
        assert "/content/1/list/2" in pointers

        assert len(pointers) == 4

    def test_get_answer_messages(self):
        schema = SurveySchema({
            "questions": [{
                "answers": [{
                    "id": "confirm-feeling-answer",
                    "type": "Radio",
                    "label": "confirm",
                    "mandatory": True,
                    "options": [
                        {
                            "value": "Yes",
                            "label": "Yes"
                        },
                        {
                            "value": "No",
                            "label": "No"
                        }
                    ]
                }]
            }]
        })

        pointers = schema.get_answer_pointers()

        assert '/questions/0/answers/0/options/0/label' in pointers
        assert '/questions/0/answers/0/options/1/label' in pointers

    def test_get_all_pointers(self):
        schema = SurveySchema({
            "content": [{
                    "title": "Include:",
                    "list": [
                        "all employees in Great Britain (England, Scotland and Wales), both full and part-time, who received pay in the relevant period"
                    ]
                },
                {
                    "title": "Exclude:",
                    "list": [
                        "trainees on government schemes",
                        "employees working abroad unless paid directly from this business’s GB payroll",
                        "employees in Northern Ireland"
                    ]
                }
            ]
        })

        assert "/content/0/title" in schema.pointers
        assert "/content/1/title" in schema.pointers
        assert "/content/0/list/0" in schema.pointers
        assert "/content/1/list/0" in schema.pointers
        assert "/content/1/list/1" in schema.pointers
        assert "/content/1/list/2" in schema.pointers

        assert len(schema.pointers) == 6

    def test_get_parent_id(self):
        schema = SurveySchema({
            "questions": [{
                "answers": [{
                    "id": "confirm-feeling-answer",
                    "type": "Radio",
                    "label": "confirm",
                    "mandatory": True,
                    "options": [
                        {
                            "value": "Yes",
                            "label": "Yes"
                        },
                        {
                            "value": "No",
                            "label": "No"
                        }
                    ]
                }]
            }]
        })

        option_parent_id = schema.get_parent_id('/questions/0/answers/0/options/0/label')
        answer_parent_id = schema.get_parent_id('/questions/0/answers/0/label')

        assert option_parent_id == 'confirm-feeling-answer'
        assert answer_parent_id == 'confirm-feeling-answer'

    def test_get_parent_question_pointer(self):

        schema = SurveySchema()

        parent_question_pointer = schema.get_parent_question_pointer('/questions/0/answers/0/options/0/label')

        assert parent_question_pointer == '/questions/0'

    def test_get_parent_question(self):
        original_question = {
            "answers": [{
                "id": "confirm-feeling-answer",
                "type": "Radio",
                "label": "confirm",
                "mandatory": True,
                "options": [
                    {
                        "value": "Yes",
                        "label": "Yes"
                    },
                    {
                        "value": "No",
                        "label": "No"
                    }
                ]
            }]
        }

        schema = SurveySchema({
            "questions": [original_question]
        })

        parent_question = schema.get_parent_question('/questions/0/answers/0/options/0/label')

        assert parent_question == original_question

    def test_translate(self):
        schema_translation = SchemaTranslation()

        catalog = Catalog()

        catalog.add("Answering for this person",
                    "WELSH - Answering for this person",
                    auto_comments=["answer-id: feeling-answer"],
                    user_comments=["Answer for: Who are you answering for??"])

        catalog.add("Answering myself",
                    "WELSH - Answering myself",
                    auto_comments=["answer-id: feeling-answer"],
                    user_comments=["Answer for: Who are you answering for??"])

        schema_translation.catalog = catalog

        schema = SurveySchema({
            "questions": [{
                "answers": [{
                    "type": "Radio",
                    "id": "feeling-answer",
                    "label": "Feeling answer",
                    "mandatory": True,
                    "options": [{
                            "label": "Answering for this person",
                            "value": "good"
                        },
                        {
                            "label": "Answering myself",
                            "value": "bad",
                            "detail_answer": {
                              "id": "feeling-bad-answer",
                              "label": "Specify why answering for yourself is bad",
                              "mandatory": True,
                              "type": "TextField"
                            }
                        }
                    ],
                    "guidance": {
                        "hide_guidance": "Hide feeling answer help",
                        "show_guidance": "Show feeling answer help",
                        "content": [{
                            "title": "Feeling answer",
                            "description": "This should be answered to see if you are answering on behalf of someone else"
                        }]
                    }
                }]
            }]
        })

        translated = schema.translate(schema_translation)

        expected = {
            "questions": [{
                "answers": [{
                    "type": "Radio",
                    "id": "feeling-answer",
                    "label": "Feeling answer",
                    "mandatory": True,
                    "options": [{
                            "label": "WELSH - Answering for this person",
                            "value": "good"
                        },
                        {
                            "label": "WELSH - Answering myself",
                            "value": "bad",
                            "detail_answer": {
                              "id": "feeling-bad-answer",
                              "label": "Specify why answering for yourself is bad",
                              "mandatory": True,
                              "type": "TextField"
                            }
                        }
                    ],
                    "guidance": {
                        "hide_guidance": "Hide feeling answer help",
                        "show_guidance": "Show feeling answer help",
                        "content": [{
                            "title": "Feeling answer",
                            "description": "This should be answered to see if you are answering on behalf of someone else"
                        }]
                    }
                }]
            }]
        }

        assert expected == translated.schema

    def test_get_catalog(self):
        schema_data = {
            "questions": [{
                "title": "Who are you answering for??",
                "answers": [{
                    "type": "Radio",
                    "id": "feeling-answer",
                    "label": "Feeling answer",
                    "mandatory": True,
                    "options": [{
                            "label": "Answering for this person",
                            "value": "good"
                        },
                        {
                            "label": "Answering myself",
                            "value": "bad",
                            "detail_answer": {
                              "id": "feeling-bad-answer",
                              "label": "Specify why answering for yourself is bad",
                              "mandatory": True,
                              "type": "TextField"
                            }
                        }
                    ],
                    "guidance": {
                        "hide_guidance": "Hide feeling answer help",
                        "show_guidance": "Show feeling answer help",
                        "content": [{
                            "title": "Feeling answer",
                            "description": "This should be answered to see if you are answering on behalf of someone else"
                        }]
                    }
                }]
            }]
        }

        schema = SurveySchema(schema_data)

        catalog = schema.get_catalog()

        actual_items = [message.id for message in catalog]

        assert schema_data['questions'][0]['title'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['label'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['options'][0]['label'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['options'][1]['label'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['options'][1]['detail_answer']['label'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['guidance']['hide_guidance'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['guidance']['show_guidance'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['guidance']['content'][0]['title'] in actual_items
        assert schema_data['questions'][0]['answers'][0]['guidance']['content'][0]['description'] in actual_items

    def test_get_catalog_uses_smart_quotes(self):
        schema_data = {
            "questions": [{
                "title": "What is 'this persons' date of birth?"
            }]
        }

        schema = SurveySchema(schema_data)

        catalog = schema.get_catalog()

        actual_items = [message.id for message in catalog]

        assert "What is ‘this persons’ date of birth?" in actual_items



