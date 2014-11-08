#!/bin/bash

# NOTE: You must execute this script from the root of the repository.

cd data
for folder in $(ls -d *)
do
    if [[ "$folder" != "common" ]]
    then
        locale="$(ls "/usr/share/i18n/locales" | grep "^$folder" | grep -v "@euro$").UTF-8"
        sudo locale-gen $locale
    fi
done