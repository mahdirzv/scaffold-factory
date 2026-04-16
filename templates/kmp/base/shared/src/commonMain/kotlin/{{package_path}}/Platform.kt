package {{package_name}}

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform