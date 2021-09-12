parserConfig = {
    "firstParsing": {
        "separatorRegex": ":|;",
        "maxSplits": 2,
        "splitSettings": [
            {
                "splits": 2,
                "fields": [
                    "username",
                    "password",
                    "email"
                ]
            }
        ],
    },
    "recursiveParsing": {
        "settings":  [
            {
                "fieldName": "email",
                "separatorRegex": "@",
                "maxSplits": 1,
                "splitSettings": [
                        {
                            "splits": 0,
                            "fields": [
                                "ignored"
                            ]
                        },
                        {
                            "splits": 1,
                            "fields": [
                                "emailLocal",
                                "emailDomain"
                            ]
                        }
                ]
            }
        ]
    },
    "outFields": [
        "username",
        "emailLocal",
        "emailDomain",
        "password"
    ]
}