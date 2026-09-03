{{- define "cvm-catalyst.fullname" -}}
{{- printf "cvm-catalyst" -}}
{{- end -}}

{{- define "cvm-catalyst.namespace" -}}
{{- .Values.global.namespace -}}
{{- end -}}
